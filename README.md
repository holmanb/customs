### Customs

A proof of concept static code analysis tool capable of identifying module
import side-effects. It uses only standard library Python modules.

Ideally this project will be replaced or subsumed by an upstream static
analysis tool.

#### Example use case

```bash
$ customs.py cloudinit/config/cc_disk_setup.py --verbose
cc_disk_setup.py:26:0: W001: Import invoked a Call | BLKID_CMD = subp.which("blkid")
cc_disk_setup.py:29:0: W001: Import invoked a Call | WIPEFS_CMD = subp.which("wipefs")
cc_disk_setup.py:111:0: W001: Import invoked a Call | __doc__ = get_meta_doc(meta)
cc_disk_setup.py:27:0: W001: Import invoked a Call | BLKDEV_CMD = subp.which("blockdev")
cc_disk_setup.py:25:0: W001: Import invoked a Call | LSBLK_CMD = subp.which("lsblk")
cc_disk_setup.py:24:0: W001: Import invoked a Call | SGDISK_CMD = subp.which("sgdisk")
cc_disk_setup.py:28:0: W001: Import invoked a Call | PARTPROBE_CMD = subp.which("partprobe")
cc_disk_setup.py:23:0: W001: Import invoked a Call | SFDISK_CMD = subp.which("sfdisk")
Analyzed 1 files

```



#### Test and maintenence

Depends on the interest by other projects such as pylint / ruff / etc.

- seek co-maintainers
- tox / pyproject.toml
- ci integration
- PyPI release?


#### Features

- inline enable / disable
- section block enable / disable
- configurable list of symbols to ignore (currently getLogger is hardcoded)
- Editor integration (VScode / NeoVim / Emacs)

Based on an analysis tool written by Tushar Sadhwani.
