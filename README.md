# OpticsPicker Price Tracker

Automated monthly price scraping for firearm optics from multiple retailers using AI.

## Features

- 🤖 AI-powered price extraction
- 📊 Multi-retailer price comparison
- 📅 Runs automatically on the 1st of every month
- 📈 Price history tracking

## How It Works

This uses Claude AI (Anthropic) to intelligently extract prices from retailer websites, even when HTML changes.

## Configuration

Edit `scraper/config.py` to add more products and retailers.

## Manual Run

Go to Actions → Monthly Price Scraper → Run workflow

## View Prices

Check `data/price_data.json` for the latest scraped prices.
