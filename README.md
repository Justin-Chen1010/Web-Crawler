# Web Crawler for a Specific Type of domain

**Version 1.0.0**

Description of the program: It is a web crawler that is built to parse through websites and retrieve specific information that we have set into a csv then at the end outputing graphs using the Pandas library.

How it works:
We first start the crawling procedure by specifying the initial page to crawl. We set up the seed URL and then look for all hyperlinks on the website, removing the index.html during the process. 

For every website that isn’t in the seed link we append them into a list “to visit” resolving to absolute URLs and not appending repeats into the list. Then while we visit each link we impose a limit just in case we break the site or get stuck in a crawler trap. While popping the first entry from the “to visit” list and accessing the website. We then append it into our visited URLs list to make sure that we don’t revisit the same website. While doing this we do another loop within the while loop, to look for all hyperlinks (by using inspect element on chrome, I found out that all hyperlinks are referenced by “a href = xxx.html”) within the new website and append new URLs that aren’t in visited URLs into our “to visit” list. 

At the same time we extract the information that we need from each of the links. In this case I have done a for loop to append the article headline and the article itself into a separate lists and numbered all of them to keep track of the information. This led me to create a csv for task 1 with the URL and Headline as written on the website itself. At this stage we have extracted all the information we need from the websites and can use the information (URL, headline, article) to complete other tasks. At this stage for Task 1 I have all 100 links with their headlines stored in a csv.