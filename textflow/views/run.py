from invoke import Collection, Program

from textflow.views import tasks

program = Program(
    namespace=Collection.from_module(tasks),
    version='0.0.0'
)

if __name__ == '__main__':
    program.run()
