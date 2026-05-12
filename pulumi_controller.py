import logging
from enum import Enum
import importlib
from pathlib import Path

MODULE_FUNCTION = "create_resource"
import boto3

import click
from pulumi import automation

PYTHON_LOGGING_FORMAT = (
    "[%(asctime)s] [%(levelname)s] "
    "[%(filename)s] [%(lineno)d] "
    "[%(threadName)s] - %(message)s"
)

logging.basicConfig(
    format=PYTHON_LOGGING_FORMAT,
    encoding="utf-8",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


class PulumiOp(Enum):
    """Supported Pulumi operations."""

    UP = "up"
    PREVIEW = "preview"
    DESTROY = "destroy"
    REFRESH = "refresh"
    CANCEL = "cancel"


class Program:
    module_name: str = ""

    def __init__(self, module_name: str = ""):
        self.module_name = module_name

    def run(self):
        # current project root
        account_id, region = self.get_aws_identity()
        root_module_name, sub_module = self.module_name.split("_", 1)
        module = self.get_module()
        getattr(module, MODULE_FUNCTION)(
            account_id,
            region,
            root_module_name,
            sub_module
        )

    def get_aws_identity(self):
        session = boto3.Session()
        account_id = session.client("sts").get_caller_identity()["Account"]
        region = session.region_name
        return account_id, region

    def get_module(self):
        base_dir = Path(__file__).resolve().parent
        modules_dir = base_dir / "modules"
        module_path = modules_dir / f"{self.module_name}.py"
        if not module_path.exists():
            raise ModuleNotFoundError(
                f"Module '{self.module_name}' not found at {self.module_path}"
            )

        module = importlib.import_module(
            f"modules.{self.module_name}"
        )

        if not hasattr(module, MODULE_FUNCTION):
            raise NotImplementedError(
                f"{self.module_name} must implement "
                f"{MODULE_FUNCTION}()"
            )

        return module


def run_program(
        op_type: PulumiOp,
        stack_name: str,
        module: str,
        debug: bool = False,
        diff: bool = False,
):
    """Run Pulumi operation for the given stack."""
    try:
        project_name = "pulumi_aws"

        program = Program(
            module_name=module,
        )

        stack = automation.select_stack(
            project_name=project_name,
            stack_name=stack_name,
            program=program.run,
        )

        stack_method_dict = {
            PulumiOp.UP: stack.up,
            PulumiOp.PREVIEW: stack.preview,
            PulumiOp.DESTROY: stack.destroy,
            PulumiOp.REFRESH: stack.refresh,
            PulumiOp.CANCEL: stack.cancel,
        }

        if op_type not in stack_method_dict:
            raise NotImplementedError(
                f"Unsupported op_type: {op_type}"
            )

        if op_type == PulumiOp.CANCEL:
            stack_method_dict[op_type]()

        elif op_type == PulumiOp.PREVIEW and diff:
            stack_method_dict[op_type](
                on_output=print,
                debug=debug,
                diff=True,
            )

        else:
            stack_method_dict[op_type](
                on_output=print,
                debug=debug,
            )

    except Exception as exc:
        logger.exception(
            "Error running %s for stack %s: %s",
            op_type.value,
            stack_name,
            exc,
        )


@click.group()
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode.",
)
@click.pass_context
def main(ctx, debug):
    """Pulumi CLI wrapper."""
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug


@main.command()
@click.option("-s", "--stack", required=True)
@click.option(
    "-m",
    "--module_name",
    type=str,
)
@click.pass_context
def up(ctx, stack, module_name):
    """Run pulumi up."""
    run_program(
        op_type=PulumiOp.UP,
        stack_name=stack,
        debug=ctx.obj["DEBUG"],
        module=module_name,
    )


@main.command()
@click.option("-s", "--stack", required=True)
@click.option(
    "-m",
    "--module_name",
    type=str,
)
@click.option(
    "--diff",
    is_flag=True,
    help="Show detailed diff for preview.",
)
@click.pass_context
def preview(ctx, stack, module_name, diff):
    """Run pulumi preview."""
    run_program(
        op_type=PulumiOp.PREVIEW,
        stack_name=stack,
        debug=ctx.obj["DEBUG"],
        module=module_name,
        diff=diff,
    )


@main.command()
@click.option("-s", "--stack", required=True)
@click.option(
    "-m",
    "--module_name",
    type=str,
)
@click.pass_context
def destroy(ctx, stack, module_name):
    """Run pulumi destroy."""
    run_program(
        op_type=PulumiOp.DESTROY,
        stack_name=stack,
        debug=ctx.obj["DEBUG"],
        module=module_name,
    )


@main.command()
@click.option("-s", "--stack", required=True)
@click.pass_context
def refresh(ctx, stack):
    """Run pulumi refresh."""
    run_program(
        op_type=PulumiOp.REFRESH,
        stack_name=stack,
        debug=ctx.obj["DEBUG"],
    )


@main.command()
@click.option("--stack", required=True)
@click.pass_context
def cancel(ctx, stack):
    """Cancel a running Pulumi operation."""
    run_program(
        op_type=PulumiOp.CANCEL,
        stack_name=stack,
        debug=ctx.obj["DEBUG"],
    )


if __name__ == "__main__":
    main()
