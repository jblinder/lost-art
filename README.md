# Lost Art: Exploring the underseen at the MFA

Attempting to understand visitor attention toward specific pieces in a museum via Instagram photos, and help curators guide viewers towards less-viewed, but by no means lesser, works.

_This project was created for Professor Kurt Fendt's MIT course ["Extending the Museum" (CMS636)](http://catalog.mit.edu/subjects/cms/)._
## Authors
- [Justin Blinder](https://www.github.com/jblinder)
- [Mulan Mu](https://github.com/Mulanmu)
- [Shayna Ahteck](https://github.com/asahteck)
## Implementation

This project combines artwork data from the Boston MFA and Instagram photos taken by vistiors to determine which works and collections are being neglected.

Currently, due to time and resource constraints, artworks are associated with Instagram photos by detecting a work author or title in an Instagram post caption. A future stage would include using an image classifer to detect artworks in photos.

**Analysis**
- `analysis/mfa-instagram-analysis.py` - Data cleaning, feature engineering, and EDA

**Data Collection**
- `scrapers/mfa.py` - scrapes on view collection works from the Boston MFA website
- `scrapers/instagram.py`  - downloads Instagram images tagged with the Boston MFA
- `scrapers/instaparser.py` - serializes Instagram metadata into flattened JSON file