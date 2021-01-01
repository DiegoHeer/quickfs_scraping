from quickfs_scraping import main

if __name__ == '__main__':
    ticker = input("Enter a valid ticker: ")
    main.app(ticker.upper())