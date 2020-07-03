import datetime
import os
import json
import shutil

timestamp_format = "%Y-%m-%dT%H_%M_%S"

powershell_send2trash = (
    "Add-Type -AssemblyName Microsoft.VisualBasic;"
    + "[Microsoft.VisualBasic.FileIO.FileSystem]::Deletedirectory('{}','OnlyErrorDialogs','SendToRecycleBin')"
)

current_dir = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(current_dir, "config.json")) as f:
    config = json.load(f)

default_target_dir = config["default_target_dir"]
default_nmax_backups = config["default_nmax_backups"]
games_data_sources = config["sources"]


def check_backups(directory, nmax_backups):
    backups_versions = os.listdir(directory)
    if len(backups_versions) > nmax_backups:
        backups_dates_map = {
            datetime.datetime.strptime(timestamp_str, timestamp_format): timestamp_str
            for timestamp_str in backups_versions
        }
        content_to_remove = backups_dates_map[min(backups_dates_map.keys())]
        path_to_remove = os.path.join(directory, content_to_remove)
        send2trash_command = powershell_send2trash.format(path_to_remove)
        os.system("powershell.exe {}".format(send2trash_command))


def backup_game_data(name, settings):
    now = datetime.datetime.utcnow()
    now_str = now.strftime(timestamp_format)

    nmax_backups = settings.get("nmax_backups", default_nmax_backups)
    target_root = settings.get("target_dir", default_target_dir)

    target_main_dir = os.path.join(target_root, name)
    target_dir_version = os.path.join(target_main_dir, now_str)

    data_paths = settings["paths"]
    for source_label, source_path in data_paths.items():
        shutil.copytree(source_path, os.path.join(target_dir_version, source_label))

    check_backups(target_main_dir, nmax_backups)


def on_game_stopped(game, elapsed_seconds):
    if game.Name in games_data_sources.keys():
        game_settings = games_data_sources[game.Name]
        backup_game_data(game.Name, game_settings)
