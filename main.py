import customtkinter as ctk
import json
import os
import threading
import time
import sys
from tkinter import messagebox
import tkinter as tk
from pythonosc import udp_client
import keyboard
import pystray
from PIL import Image, ImageDraw, ImageTk


def get_resource_path(relative_path):
    """リソースファイルの絶対パスを取得（EXE化対応）"""
    try:
        # PyInstallerで作成されたEXEの場合
        base_path = sys._MEIPASS
    except AttributeError:
        # 開発環境の場合
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


class VRChatMuteController:
    def __init__(self):
        # OSC設定
        self.osc_ip = "127.0.0.1"
        self.osc_port = 9000
        self.osc_client = udp_client.SimpleUDPClient(self.osc_ip, self.osc_port)
        
        # 設定ファイル
        self.config_file = "vrchat_mute_config.json"
        
        # ショートカット設定
        self.mute_toggle_shortcut = ""
        
        # フォント設定
        self.font_family = "Meslo"
        self.font_size = 12
        
        # UI初期化
        self.setup_ui()
        
        # 設定読み込み
        self.load_config()
        
        # ショートカット監視開始
        self.start_hotkey_listener()
        
        # システムトレイ
        self.setup_system_tray()
    
    def setup_ui(self):
        # ダークテーマ設定
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # メインウィンドウ
        self.window = ctk.CTk()
        self.window.title("VRChat Mute Controller")
        self.window.geometry("600x600")
        self.window.configure(fg_color="#1a1a1a")
        
        # ステップ1: 基本的なアイコン設定
        self.setup_window_icon()
        
        # ウィンドウを閉じる時の処理
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # メインフレーム
        main_frame = ctk.CTkFrame(self.window, fg_color="#2a2a2a")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # タイトル
        title_label = ctk.CTkLabel(
            main_frame, 
            text="VRChat Mute Controller",
            font=(self.font_family, 20, "bold"),
            text_color="#ffffff"
        )
        title_label.pack(pady=10)
        
        # 警告メッセージ
        warning_frame = ctk.CTkFrame(main_frame, fg_color="#3a2a2a")
        warning_frame.pack(fill="x", padx=10, pady=5)
        
        warning_label = ctk.CTkLabel(
            warning_frame,
            text="⚠️ VRChatの設定でマイクの動作を\"切り替え\"にして使用してください。",
            font=(self.font_family, 11),
            text_color="#ffaa00",
            justify="left"
        )
        warning_label.pack(pady=10)
        
        # ショートカット設定エリア
        shortcut_frame = ctk.CTkFrame(main_frame, fg_color="#333333")
        shortcut_frame.pack(fill="x", padx=10, pady=10)
        
        # ミュートトグル設定
        mute_toggle_label = ctk.CTkLabel(
            shortcut_frame,
            text="ミュート切り替えショートカット:",
            font=(self.font_family, self.font_size),
            text_color="#ffffff"
        )
        mute_toggle_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.mute_toggle_entry = ctk.CTkEntry(
            shortcut_frame,
            placeholder_text="例: f12, ctrl+shift+m",
            font=(self.font_family, self.font_size),
            width=400
        )
        self.mute_toggle_entry.pack(padx=10, pady=(0, 10))
        
        # デフォルト値を設定
        self.mute_toggle_entry.insert(0, "f12")
        
        # ボタンフレーム
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # 設定保存ボタン
        save_button = ctk.CTkButton(
            button_frame,
            text="設定を保存",
            command=self.save_config,
            font=(self.font_family, self.font_size),
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        save_button.pack(side="left", padx=5)
        
        # 設定読み込みボタン
        load_button = ctk.CTkButton(
            button_frame,
            text="設定を読み込み",
            command=self.load_config,
            font=(self.font_family, self.font_size),
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        load_button.pack(side="left", padx=5)
        
        # ショートカット再設定ボタン
        reload_button = ctk.CTkButton(
            button_frame,
            text="ショートカット再設定",
            command=self.reload_shortcuts,
            font=(self.font_family, self.font_size),
            fg_color="#FF9800",
            hover_color="#F57C00"
        )
        reload_button.pack(side="left", padx=5)
        
        # 状態表示エリア
        status_frame = ctk.CTkFrame(main_frame, fg_color="#333333")
        status_frame.pack(fill="x", padx=10, pady=10)
        
        status_title = ctk.CTkLabel(
            status_frame,
            text="動作状態:",
            font=(self.font_family, 14, "bold"),
            text_color="#ffffff"
        )
        status_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="待機中...",
            font=(self.font_family, self.font_size),
            text_color="#00ff00"
        )
        self.status_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # OSC情報表示
        osc_info_frame = ctk.CTkFrame(main_frame, fg_color="#333333")
        osc_info_frame.pack(fill="x", padx=10, pady=10)
        
        osc_info_label = ctk.CTkLabel(
            osc_info_frame,
            text=f"OSC設定: {self.osc_ip}:{self.osc_port}",
            font=(self.font_family, 11),
            text_color="#888888"
        )
        osc_info_label.pack(pady=10)
        
        # 使用方法
        usage_frame = ctk.CTkFrame(main_frame, fg_color="#333333")
        usage_frame.pack(fill="x", padx=10, pady=10)
        
        usage_title = ctk.CTkLabel(
            usage_frame,
            text="使用方法:",
            font=(self.font_family, 14, "bold"),
            text_color="#ffffff"
        )
        usage_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        usage_text = """1. VRChatでOSC機能を有効にしてください
2. VRChatの設定でマイクの動作を「切り替え」に設定してください
3. ショートカットを設定して「設定を保存」をクリック
4. 設定したショートカットでミュートの切り替えができます"""
        
        usage_label = ctk.CTkLabel(
            usage_frame,
            text=usage_text,
            font=(self.font_family, 10),
            text_color="#cccccc",
            justify="left"
        )
        usage_label.pack(anchor="w", padx=10, pady=(0, 10))
    
    def setup_system_tray(self):
        """システムトレイアイコンの設定"""
        # アイコンファイルを読み込み
        try:
            icon_path = get_resource_path("icon.ico")
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
            else:
                # フォールバック: デフォルトアイコンを作成
                image = Image.new('RGB', (64, 64), color='black')
                draw = ImageDraw.Draw(image)
                draw.ellipse([16, 16, 48, 48], fill='white')
        except Exception:
            # エラーの場合はデフォルトアイコンを作成
            image = Image.new('RGB', (64, 64), color='black')
            draw = ImageDraw.Draw(image)
            draw.ellipse([16, 16, 48, 48], fill='white')
        
        # トレイメニュー
        menu = pystray.Menu(
            pystray.MenuItem("表示", self.show_window),
            pystray.MenuItem("終了", self.quit_app)
        )
        
        self.tray_icon = pystray.Icon(
            "VRChat Mute Controller",
            image,
            menu=menu
        )
    
    def start_hotkey_listener(self):
        """ショートカット監視を開始"""
        # 初期化時にはショートカットを設定しない
        self.update_status("ショートカット監視を開始しました")
    
    def hotkey_listener(self):
        """ショートカットを監視（使用しない）"""
        # この関数は使用しない
        pass
    
    def mute_toggle(self):
        """ミュートトグル"""
        try:
            # 1を送信してからすぐに0を送信
            self.osc_client.send_message("/input/Voice", 1)
            time.sleep(0.1)  # 100ms待機
            self.osc_client.send_message("/input/Voice", 0)
            self.update_status("ミュート切り替えメッセージを送信しました")
        except Exception as e:
            self.update_status(f"送信エラー: {str(e)}")
    
    def update_status(self, message):
        """状態表示を更新"""
        def update():
            self.status_label.configure(text=f"{time.strftime('%H:%M:%S')} - {message}")
        
        if self.window.winfo_exists():
            self.window.after(0, update)
    
    def save_config(self):
        """設定を保存"""
        config = {
            "mute_toggle_shortcut": self.mute_toggle_entry.get()
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.update_status("設定を保存しました")
            messagebox.showinfo("保存完了", "設定が保存されました")
            
            # ショートカットを再設定（遅延実行）
            self.window.after(100, self.reload_shortcuts)
            
        except Exception as e:
            self.update_status(f"設定保存エラー: {str(e)}")
            messagebox.showerror("エラー", f"設定の保存に失敗しました: {str(e)}")
    
    def load_config(self):
        """設定を読み込み"""
        if not os.path.exists(self.config_file):
            self.update_status("設定ファイルが見つかりません - デフォルト値を使用")
            # デフォルト値を設定
            self.mute_toggle_entry.delete(0, 'end')
            self.mute_toggle_entry.insert(0, "f12")
            # ショートカットを設定（遅延実行）
            self.window.after(100, self.reload_shortcuts)
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.mute_toggle_entry.delete(0, 'end')
            self.mute_toggle_entry.insert(0, config.get("mute_toggle_shortcut", ""))
            
            self.update_status("設定を読み込みました")
            
            # ショートカットを再設定（遅延実行）
            self.window.after(100, self.reload_shortcuts)
            
        except Exception as e:
            self.update_status(f"設定読み込みエラー: {str(e)}")
            messagebox.showerror("エラー", f"設定の読み込みに失敗しました: {str(e)}")
    
    def reload_shortcuts(self):
        """ショートカットを再設定"""
        try:
            # 既存のショートカットをクリア
            try:
                keyboard.clear_all_hotkeys()
            except:
                # エラーが発生した場合は無視
                pass
            
            # 新しいショートカットを設定
            mute_toggle = self.mute_toggle_entry.get().strip()
            
            if mute_toggle:
                try:
                    keyboard.add_hotkey(mute_toggle, self.mute_toggle)
                    self.update_status("ショートカットを再設定しました")
                except Exception as e:
                    self.update_status(f"ショートカット設定エラー: {str(e)}")
            else:
                self.update_status("ショートカットが設定されていません")
            
        except Exception as e:
            self.update_status(f"ショートカット設定エラー: {str(e)}")
            messagebox.showerror("エラー", f"ショートカットの設定に失敗しました: {str(e)}")
    
    def on_closing(self):
        """ウィンドウを閉じる時の処理"""
        self.window.withdraw()  # ウィンドウを隠す
        self.tray_icon.run_detached()  # トレイアイコンを表示
    
    def show_window(self, icon=None, item=None):
        """ウィンドウを表示"""
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
    
    def quit_app(self, icon=None, item=None):
        """アプリケーションを終了"""
        try:
            # ホットキーをクリア
            keyboard.clear_all_hotkeys()
        except:
            pass
        
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        
        self.window.quit()
        self.window.destroy()
    
    def setup_window_icon(self):
        """ステップバイステップでウィンドウアイコンを設定"""
        icon_path = get_resource_path("icon.ico")
        
        # ステップ1: アイコンファイルの存在確認
        if not os.path.exists(icon_path):
            print(f"⚠️ アイコンファイルが見つかりません: {icon_path}")
            return
            
        # ステップ2: ファイルサイズ確認
        file_size = os.path.getsize(icon_path)
        print(f"📄 アイコンファイルサイズ: {file_size} bytes")
        
        if file_size < 1000:
            print("⚠️ アイコンファイルが小さすぎる可能性があります")
        
        # ステップ3: CustomTkinterウィンドウの更新を待つ
        self.window.update_idletasks()
        
        # ステップ4: 基本的なtkinterアイコン設定
        try:
            self.window.iconbitmap(icon_path)
            print("✅ iconbitmap設定完了")
        except Exception as e:
            print(f"❌ iconbitmap設定エラー: {e}")
        
        # ステップ5: 即座に追加設定を試行
        self.apply_immediate_icon_settings(icon_path)
        
        # ステップ6: 遅延実行でさらなる設定
        self.window.after(50, lambda: self.apply_additional_icon_settings(icon_path))
        self.window.after(200, lambda: self.apply_additional_icon_settings(icon_path))
        self.window.after(500, lambda: self.apply_additional_icon_settings(icon_path))
    
    def apply_immediate_icon_settings(self, icon_path):
        """即座にアイコン設定を適用"""
        try:
            # CustomTkinterの内部tkinterウィンドウにアクセス
            root_window = self.window.winfo_toplevel()
            
            # wm_iconbitmapを即座に設定
            root_window.wm_iconbitmap(icon_path)
            print("✅ 即座wm_iconbitmap設定完了")
            
            # tkinterウィンドウのアトリビュートを直接操作
            if hasattr(root_window, 'tk'):
                root_window.tk.call('wm', 'iconbitmap', root_window._w, icon_path)
                print("✅ tk.call経由のアイコン設定完了")
            
        except Exception as e:
            print(f"❌ 即座アイコン設定エラー: {e}")
    
    def apply_additional_icon_settings(self, icon_path):
        """追加のアイコン設定を適用"""
        try:
            # CustomTkinterの内部tkinterウィンドウにアクセス
            root_window = self.window.winfo_toplevel()
            
            # wm_iconbitmapも試行
            try:
                root_window.wm_iconbitmap(icon_path)
                print("✅ wm_iconbitmap設定完了")
            except Exception as e:
                print(f"❌ wm_iconbitmap設定エラー: {e}")
            
            # iconphoto（PNG形式）も試行
            try:
                from PIL import Image
                icon_image = Image.open(icon_path)
                # 最初の画像（通常は最大サイズ）を使用
                if hasattr(icon_image, 'size'):
                    photo = ImageTk.PhotoImage(icon_image)
                    root_window.iconphoto(True, photo)
                    # 参照を保持してガベージコレクションを防ぐ
                    self.icon_photo_ref = photo
                    print("✅ iconphoto設定完了")
            except Exception as e:
                print(f"❌ iconphoto設定エラー: {e}")
                
            # 強制的にウィンドウを更新
            try:
                root_window.update_idletasks()
                root_window.update()
                print("✅ ウィンドウ更新完了")
            except Exception as e:
                print(f"❌ ウィンドウ更新エラー: {e}")
                
        except Exception as e:
            print(f"❌ 追加アイコン設定エラー: {e}")

    def run(self):
        """アプリケーションを実行"""
        print("🚀 アプリケーション開始")
        
        # ウィンドウ表示後にアイコンを再設定
        icon_path = get_resource_path("icon.ico")
        self.window.after(1000, lambda: self.force_icon_update(icon_path))
        self.window.after(2000, lambda: self.force_icon_update(icon_path))
        
        self.window.mainloop()
    
    def force_icon_update(self, icon_path):
        """強制的にアイコンを更新"""
        try:
            print("🔄 アイコン強制更新実行")
            root_window = self.window.winfo_toplevel()
            
            # 複数の方法でアイコンを設定
            root_window.iconbitmap(icon_path)
            root_window.wm_iconbitmap(icon_path)
            
            # Tkinterの低レベルコマンドを使用
            if hasattr(root_window, 'tk'):
                root_window.tk.call('wm', 'iconbitmap', root_window._w, icon_path)
            
            # ウィンドウマネージャーに強制的に更新を通知
            root_window.update_idletasks()
            root_window.update()
            
            print("✅ アイコン強制更新完了")
        except Exception as e:
            print(f"❌ アイコン強制更新エラー: {e}")


if __name__ == "__main__":
    try:
        app = VRChatMuteController()
        app.run()
    except Exception as e:
        print(f"アプリケーション起動エラー: {str(e)}")
        messagebox.showerror("起動エラー", f"アプリケーションの起動に失敗しました: {str(e)}")