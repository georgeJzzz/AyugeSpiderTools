import os
import string
from pathlib import Path
from os.path import join, exists, abspath
from shutil import copy2, copystat, ignore_patterns, move
from stat import S_IWUSR as OWNER_WRITE_PERMISSION

from scrapy.exceptions import UsageError
from scrapy.utils.template import render_templatefile, string_camelcase

import ayugespidertools
from scrapy.commands.startproject import Command


TEMPLATES_TO_RENDER = (
    ("scrapy.cfg",),
    ("${project_name}", "settings.py.tmpl"),
    ("${project_name}", "items.py.tmpl"),
    ("${project_name}", "pipelines.py.tmpl"),
    ("${project_name}", "middlewares.py.tmpl"),
    # 添加 run.py 总运行文件
    ("${project_name}", "run.py.tmpl"),
)

IGNORE = ignore_patterns("*.pyc", "__pycache__", ".svn")


def _make_writable(path):
    current_permissions = os.stat(path).st_mode
    os.chmod(path, current_permissions | OWNER_WRITE_PERMISSION)


class AyuCommand(Command):

    requires_project = False
    default_settings = {"LOG_ENABLED": False, "SPIDER_LOADER_WARN_ONLY": True}

    def run(self, args, opts):
        if len(args) not in (1, 2):
            raise UsageError()

        project_name = args[0]

        if len(args) == 2:
            project_dir = Path(args[1])
        else:
            project_dir = Path(args[0])

        if (project_dir / "scrapy.cfg").exists():
            self.exitcode = 1
            print(f"Error: scrapy.cfg already exists in {project_dir.resolve()}")
            return

        if not self._is_valid_name(project_name):
            self.exitcode = 1
            return

        self._copytree(Path(self.templates_dir), project_dir.resolve())
        move(project_dir / "module", project_dir / project_name)
        for paths in TEMPLATES_TO_RENDER:
            tplfile = Path(
                project_dir,
                *(
                    string.Template(s).substitute(project_name=project_name)
                    for s in paths
                ),
            )
            render_templatefile(
                tplfile,
                project_name=project_name,
                ProjectName=string_camelcase(project_name),
            )

        # 添加执行 shell 文件 run.sh 的生成
        render_templatefile(
            f"{project_dir}/{project_dir}/run.sh.tmpl",
            project_startup_dir=abspath(project_dir),
            ProjectStartupDir=string_camelcase(abspath(project_dir)),
            project_name=project_name,
            ProjectName=string_camelcase(project_name)
        )
        print(
            f"New Scrapy project '{project_name}', using template directory "
            f"'{self.templates_dir}', created in:"
        )
        print(f"    {project_dir.resolve()}\n")
        print("You can start your first spider with:")
        print(f"    cd {project_dir}")
        print("    scrapy genspider example example.com")
        # 添加本库的文字提示内容
        print("Or you can start your first spider with ayugespidertools:")
        print("    ayugespidertools genspider example example.com")

    @property
    def templates_dir(self) -> str:
        # 修改 startproject 模板文件路径为 ayugespidertools 的自定义路径
        return str(
            Path(
                Path(ayugespidertools.__path__[0], "templates"),
                "project",
            )
        )
