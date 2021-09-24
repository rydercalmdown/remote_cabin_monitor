import logging
from monitor import Monitor


def main():
    """Run the application"""
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    monitor = Monitor()
    monitor.run()


if __name__ == '__main__':
    main()
