from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

class MultipleProgress(Progress):
    def get_renderables(self):
        for task in self.tasks:
            if task.fields.get("progress_type") == "total":
                self.columns = (
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    TextColumn("{task.completed}/{task.total}"),
                    TimeElapsedColumn(),
                    TimeRemainingColumn(),
                )
            elif task.fields.get("progress_type") == "download":
                self.columns = (
                    TextColumn("[bold blue]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    DownloadColumn(),
                    TransferSpeedColumn(),
                    TimeElapsedColumn(),
                    TimeRemainingColumn(),
                )
            yield self.make_tasks_table([task])
