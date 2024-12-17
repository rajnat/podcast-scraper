from podcast_scraper.process import process_urls
#from podcast_scraper.scrape import scrape_episode_links


if __name__ == "__main__":
    input_file = "data/episodes.txt"  # File containing podcast page URLs
    iframe_xpath = "//iframe[contains(@src, 'simplecast.com')]"
    element_xpath = "//a[contains(@href, '.mp3')]"  # Update based on your structure
    output_dir = "data/output"  # Directory to save outputs

    process_urls(input_file, iframe_xpath, element_xpath, output_dir)


# # Example usage
# if __name__ == "__main__":
#     page_url = "https://www.econlib.org/econtalk-archives-by-date/?selected_year=2006#content"  # Replace with the actual webpage URL
#     xpath = "/html/body/section[2]/div/div/article/div[2]/h3/a"
#     episode_links = scrape_episode_links(page_url, xpath)
#     print(episode_links)