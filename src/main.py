# src/main.py
import asyncio
from src.config.settings import Settings
from src.ui.dashboard import Dashboard
from src.utils.logging import get_logger

logger = get_logger(__name__)

async def main():
    try:
        # Load settings
        settings = Settings()
        
        # Initialize dashboard
        dashboard = Dashboard(settings)
        
        # Run the dashboard
        logger.info("Starting ShekaraCode dashboard...")
        dashboard.run(debug=settings.debug)
        
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())