# Treasury Take Home Assignment

## Interview Notes
- Reviews about 150,000 labels a year
- Wants an application that can verify an application matches a label
    - Brand name
    - ABV
    - Government warning
        - Must be word-for-word.
        - GOVERNMENT WARNING in all caps and bold
- Must return results within 5 seconds
- Simple, easy use. Clean and obvious buttons
- Strong desire: Batch uploads (sometimes they get 200-300 applications at once)
- Make a stand alone proof on concept project
- No sensitive data being stored for this prototype
- Their network blocks outbound traffic to most domains
- Can’t just pattern match
    - Ex. “STONE THROW” on the label and “Stone Throw” from the application need to be identified as the same
- Stretch goal: AI could handles poor photographed labels, bad lighting, and glares
- Reject and ask for a better image


Additional Notes:
- TBB information for specific labeling by beverage type: https://www.ttb.gov/regulated-commodities/labeling/labeling-resources 
- Malt beverage: https://www.ttb.gov/regulated-commodities/beverage-alcohol/beer/labeling
- Distilled spirits: https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/labeling 
- Wine: https://www.ttb.gov/regulated-commodities/beverage-alcohol/wine/labeling 
- Other common elements:
    - **Brand name**
    - **Class/type designation**
    - **Alcohol content (with some exceptions for certain wine/beer)**
    - **Net contents**
    - Name and address of bottler/producer
    - Country of origin for imports
    - **Government Health Warning Statement (mandatory on all alcohol beverages)**
    **Mandatory for this project**
- Encouraged to create or source additional test labels with AI generation tools
