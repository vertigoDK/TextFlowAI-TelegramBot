from app.core.services.container import Container

async def main() -> None:
    container = Container() 


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
