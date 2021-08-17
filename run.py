import os
import sys
import time

import click

from app import create_app
from config import app_config


@click.group()
@click.argument("test_plan")
@click.pass_context
def cli(ctx, test_plan):
    ctx.ensure_object(dict)
    ctx.obj["TEST_PLAN"] = test_plan.lower()


@cli.command()
@click.option("--loop", is_flag=True)
@click.option("--mode")
@click.pass_context
def run(ctx, loop, mode=None):
    plan = ctx.obj["TEST_PLAN"]
    config = app_config[plan]
    if mode:
        config.TEST_MODE = mode
    app = create_app(config)
    if loop:
        while True:
            app.run()
            print("Sleeping...")
            time.sleep(config.SLEEP_INTERVAL)
    app.run()


@cli.command()
@click.pass_context
def reset(ctx):
    plan = ctx.obj["TEST_PLAN"]
    config = app_config[plan]
    app = create_app(config)
    print(f"Resetting all tests for {plan}...")
    app.publisher.reset_tests()
    print("Tests reset")


if __name__ == "__main__":
    cli()
