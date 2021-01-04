from quickfs_scraping import process

if __name__ == '__main__':
    ticker = input("Enter a valid ticker: ")
    process.run(ticker.upper())
