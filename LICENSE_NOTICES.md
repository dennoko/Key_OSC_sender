# License Notices

This project uses the following third-party libraries. Each library's license is listed below.

## Third-Party Libraries

### customtkinter
- **Version**: 5.2.0
- **License**: MIT License
- **Author**: Tom Schimansky
- **Homepage**: https://customtkinter.tomschimansky.com
- **Repository**: https://github.com/TomSchimansky/CustomTkinter
- **License Details**: MIT License allows unrestricted use, modification, and distribution.

### python-osc
- **Version**: 1.8.1
- **License**: Unlicense (Public Domain)
- **Author**: attwad
- **Repository**: https://github.com/attwad/python-osc
- **License Details**: Unlicensed - do what you want with it. No restrictions.

### keyboard
- **Version**: 0.13.5
- **License**: MIT License
- **Author**: BoppreH
- **Repository**: https://github.com/boppreh/keyboard
- **License Details**: MIT License allows unrestricted use, modification, and distribution.

### pystray
- **Version**: 0.19.4
- **License**: LGPL-3.0 (GNU Lesser General Public License v3.0)
- **Author**: Moses Palmér
- **Repository**: https://github.com/moses-palmer/pystray
- **License Details**: LGPL-3.0 requires that derivative works be available under the same license. However, applications that use the library as a separate component are not considered derivative works.

### Pillow (PIL Fork)
- **Version**: 11.3.0
- **License**: MIT-CMU License (MIT-like)
- **Author**: Jeffrey A. Clark and contributors
- **Repository**: https://github.com/python-pillow/Pillow
- **License Details**: MIT-style license allows unrestricted use, modification, and distribution.

### setuptools
- **Version**: 80.9.0
- **License**: MIT License
- **Author**: Python Packaging Authority
- **License Details**: MIT License allows unrestricted use, modification, and distribution.

### PyInstaller
- **Version**: 6.14.2
- **License**: GPL-2.0-or-later with special exception
- **Authors**: Hartmut Goebel, Giovanni Bajo, David Vierra, David Cortesi, Martin Zibricky
- **Repository**: https://github.com/pyinstaller/pyinstaller
- **License Details**: GPL-2.0 license with a special exception that allows PyInstaller to be used to build and distribute non-free programs (including commercial ones).

## Important Notes

### LGPL-3.0 (pystray)
The pystray library is licensed under LGPL-3.0. This means:
- You can use this library in proprietary applications
- You must provide notice that you are using LGPL-licensed code
- If you modify the pystray library itself, those modifications must be made available under LGPL-3.0
- Since we use pystray as a separate library (not modifying it), our application is not required to be open source

### GPL-2.0 with Exception (PyInstaller)
PyInstaller is licensed under GPL-2.0 but includes a special exception:
- The special exception allows PyInstaller to be used to build and distribute non-free programs
- This means you can use PyInstaller to create commercial applications
- The exception specifically addresses the bundling of Python code with the PyInstaller bootloader

## Compliance Requirements

To comply with the licenses:

1. **Include this license notice file** with your distribution
2. **Maintain copyright notices** for all libraries
3. **No modifications** to the third-party libraries themselves (we use them as-is)
4. **LGPL compliance**: Since we use pystray as a separate library without modification, we only need to provide proper attribution

## Full License Texts

For complete license texts, please refer to:
- MIT License: https://opensource.org/licenses/MIT
- LGPL-3.0: https://www.gnu.org/licenses/lgpl-3.0.html
- Unlicense: https://unlicense.org/
- GPL-2.0: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

## Distribution Requirements

When distributing this software:
1. Include this `LICENSE_NOTICES.md` file
2. Include the main project license file (`LICENSE` or similar)
3. No additional requirements due to our usage pattern of the libraries

---

**Note**: This license notice was generated on 2025-07-06. Library versions and licenses may change over time. Always verify current license information when updating dependencies.
