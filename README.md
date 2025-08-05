# Summarize Demographics ArcGIS Tool - beta version

Megan Kung, Equity Data Specialist, OPEETA, State Water Resources Control Board, megan.kung\@waterboards.ca.gov

### Overview

Areas of interest to the Water Boards often do not align with Census-designated boundaries, making it difficult to estimate the demographics of a population within areas being considered for Water Board actions, such as watersheds, drinking water systems, or contaminated groundwater plumes. Following the methodology of USEPA's EJScreen version 2.3 ([mirror site](https://pedp-ejscreen.azurewebsites.net/)), the Water Boards' ArcGIS Summarize Demographics tool allows staff to easily create demographic summaries for one or multiple areas of interest.

Specifically, the tool estimates total population and population-weighted averages of 2023 median household income, race, and languages spoken at home for those who speak English "not very well" within user-specified boundaries.

### Files in zipped CA_Demographic_Analysis folder

-   **CA_Demographic_Analysis_layers.lpkx** - layer package that contains three layers: CA_Demographics_2023, Tribal_Lands_and_Tracts, and Demographics_analysis_layer_2023

-   **Summarize_Demographics.atbx** - toolbox that contains Summarize Demographics tool

-   **Summarize_Demographics_code.py** - Python code for the Summarize Demographics tool

### Package layers

The **CA_Demographics_2023** layer contains data on 2023 median household income, race, and languages spoken at home for those who speak English "not very well". This data was compiled from the 5-year 2019-2023 U.S. Census American Community Survey. Also included is a variable for disadvantaged community status by block group. The definition of disadvantaged community follows Water Code 79505.5, where a community with an annual median household income less than 80% of the statewide median household income is considered disadvantaged, and a community with an annual median income less than 60% is considered severely disadvantaged. Income and race data were collected at the block group level, and language data was collected at the census tract level.

The **Tribal_Lands_and_Tracts** layer is a union of two layers, PRO_Indian_Lands and PRO_Tracts_All, from the Pacific Region Office of the Bureau of Indian Affairs.

**Demographic_analysis_layer_2023** is a compilation of 2020 block-level population data and 2023 data from the CA_Demographics layer. This layer is what the Summarize Demographics tool utilizes for its estimates. In most cases, the user can ignore this layer.

### Setup

1)  Download the zipped 'CA_Demographic_Analysis' folder and extract files to your working folder. Open ArcGIS Pro. In the Catalog pane, right-click 'Folders' and click 'Add Folder Connection' to add the working folder where you saved the data. Be sure to select the *folder* that contains the files and not any particular file. In the 'CA_Demographic_Analysis' folder, you will see the 'Summarize_Demographics' toolbox and the 'CA_Demographic_Analysis_layers' package.

    <img src="https://github.com/user-attachments/assets/cf91ca01-751d-4b10-9193-d41b91ae5200" alt="Image" width="1371" height="818"/>

2)  To view the layers in the layer package, drag and drop 'CA_Demographic_Analysis_layers.lpkx' onto the map. Also, click on the triangle next to the 'Summarize_Demographics' toolbox to show the 'Summarize Demographics' tool underneath.

    <img src="https://github.com/user-attachments/assets/a19559cf-21b8-4aea-9df4-6eb65f120ef5" alt="Image" width="1415" height="845"/>

3)  Assuming you already have shapefiles (.shp) or geodatabase (.gdb) files for your boundaries of interest, connect to where those files are located by right-clicking on 'Folders' in the Catalog pane again, click on 'Add Folder Connection' and select the relevant folder. Drag and drop your boundary file to add to the map. For this example, we're using the watershed area boundaries of the Safe Clean Water Program, which funds stormwater projects in Los Angeles County.

    **Note**: analysis boundaries that are bigger than at least several block groups are most appropriate for use with this tool. Boundaries that are smaller will lead to highly uncertain estimates. Also, the tool can take some time to process depending on the number of polygons in your boundary file, as well as how big the polygons are. A suggested maximum for the number of polygons in your analysis boundary file would be 150.

    <img src="https://github.com/user-attachments/assets/5a328fb1-0ae2-4c57-976b-27d4a2e4785a" alt="Image" width="1372" height="821"/>

4)  If your analysis boundary is a shapefile (.shp), it needs to be changed into a geodatabase (.gdb) file. To identify the type of file, you can hover your cursor over the file in the Catalog pane to view a pop-up window with file information. Next to "Type" it will say if the file is a "Shapefile" or "File Geodatabase Feature Class". If your analysis boundary is already a geodatabase file, skip to the next step. Otherwise, in the Contents pane, right-click on the analysis boundary layer, hover over 'Data', then select 'Export Features'. Export the layer to your project geodatabase, called "MyProject1" in this example, and the file will be saved as a .gdb file.

    <img src="https://github.com/user-attachments/assets/5200cb79-fe1c-4c6c-a6c5-6a3997b3021b" alt="Image" width="1374" height="821"/>

    <img src="https://github.com/user-attachments/assets/78f3fb64-83c8-47ad-a202-71c85b577fbb" alt="Image" width="1373" height="821"/>

5)  Double-click on the Summarize Demographics tool. Fill in the parameter fields, described in pop-up fields if you hover over the red asterisk. Parameters are also described in the following 'Tool Parameters' section. For 'Analysis ID', choose the field you would like to see exported in the summary output file. This field must be text and unique, i.e. each ID value can only appear once. (To view the attribute table of your analysis boundary layer, right-click on the layer in the Contents pane and right-click 'Attribute Table'.) For this example, we'll use the 'Watershed\_' field. Click 'Run', cross your fingers, and say a prayer to the GIS gods.

    <img src="https://github.com/user-attachments/assets/6ded38de-9128-4797-98bf-81689f794da8" alt="Image" width="1371" height="818"/>

6)  If all goes well, it should create an Excel report of summary demographic statistics exported to the folder you specified in the tool.

    <img src="https://github.com/user-attachments/assets/5337fa6f-ab38-43a5-a6f4-c7d69cad36b7" alt="Image" width="1437" height="736"/>

### Tool Parameters

-   **Analysis boundaries** - feature layer of single or multiple boundaries on which to summarize demographics. Layer must be shapefile or geodatabase file.
-   **Analysis ID** - ID variable from the analysis boundaries layer over which to summarize. Field must be text and unique, meaning each ID value can only appear once.
-   **Export file** - filename and location for summary output.

### Apportionment

When the user specifies analysis boundaries that do not align with Census boundaries, Census polygons will fall partially within and outside the analysis boundaries. The Summarize Demographics tool accounts for this by apportioning based on population weighting at the Census block level, following the methodology of US EPA's EJScreen version 2.3 ([mirror site](https://pedp-ejscreen.azurewebsites.net/)). Note that as long as the user chooses analysis boundaries much larger than one block group, estimates should be reasonably representative of the population within the boundaries. Use caution with analysis boundaries that are about the size of only a few block groups or smaller. More details can be found in the [EJScreen Technical Documentation](https://www.epa.gov/system/files/documents/2024-07/ejscreen-tech-doc-version-2-3.pdf) under the Buffer Reports section.

### Tips

-   Analysis ID variable must be unique and in text format.
-   Make sure there are no spaces in your analysis layer name.
-   Analysis boundaries that are bigger than at least several block groups are most appropriate for use with this tool. Boundaries that are smaller will lead to highly uncertain estimates. The 'num_of_blocks' field in the output table is an indicator for the level of certainty. Boundaries with only a few blocks will have highly uncertain estimates, whereas boundaries with a high number of blocks will be relatively accurate.
-   A suggested maximum for the number of polygons in your analysis boundary file would be 150. The tool can take some time to process depending on the number of polygons in your boundary file, as well as how big the polygons are.

### Notes

-   CalEnviroscreen 4.0 scores were not incorporated due to its use of 2019 data, which was based on Census boundaries that differ from 2023. OPEETA staff plan on incorporating CES scores when CalEnviroscreen is next updated.
-   Language percent variables reflect percent of total households. OPEETA staff plan on incorporating language variables as percent of limited-English speaking households in the next release.
-   The summarized MHI23 (median household income 2023) value in the tool output is the population-weighted mean value of median household income. Due to data limitations, the actual median household income is not estimated, but the estimated mean income value is a reasonable approximation. In areas where the income distribution is more skewed, i.e. there are relatively few people with incomes that are much higher or lower than everyone else, the mean value will differ more from the median.

### Data Dictionary

| Variable | Description |
|------------------------------------|------------------------------------|
| TotalPop | Total population |
| MHI23 | Median Household Income |
| White | White (non-Hispanic) |
| Black | Black (non-Hispanic) |
| AmerInd | American Indian (non-Hispanic) |
| Asian | Asian (non-Hispanic) |
| PacIsl | Pacific Islander (non-Hispanic) |
| Other | Other (non-Hispanic) |
| Mixed | Mixed race (non-Hispanic) |
| Hisp | Hispanic |
| White_Perc | Percent white (non-Hispanic) |
| Black_Perc | Percent Black (non-Hispanic) |
| AmerInd_Perc | Percent American Indian (non-Hispanic) |
| Asian_Perc | Percent Asian (non-Hispanic) |
| PacIsl_Perc | Percent Pacific Islander (non-Hispanic) |
| Other_Perc | Percent Other race (non-Hispanic) |
| Mixed_Perc | Percent mixed race (non-Hispanic) |
| Hisp_Perc | Percent Hispanic |
| English_Only_Perc | Percent households where only English is spoken |
| Spanish_Perc | Percent Spanish-speaking households where English is spoken "not very well" |
| French_Haitian_Cajun_Perc | Percent French, Haitian, and Cajun-speaking households where English is spoken "not very well" |
| German_WestGermanic_Perc | Percent German and West-Germanic-speaking households where English is spoken "not very well" |
| Russian_Polish_Slavic_Perc | Percent Russian, Polish, and Slavic-speaking households where English is spoken "not very well" |
| OtherIndoEuro_Perc | Percent other Indo-European-speaking households where English is spoken "not very well" |
| Korean_Perc | Percent Korean-speaking households where English is spoken "not very well" |
| Chinese_Perc | Percent Chinese-speaking households where English is spoken "not very well" |
| Vietnamese_Perc | Percent Vietnamese-speaking households where English is spoken "not very well" |
| Tagalog_incl_Filipino_Perc | Percent Tagalog including Filipino-speaking households where English is spoken "not very well" |
| OtherAsianPacIsl_Perc | Percent other Asian Pacific Islander-speaking households where English is spoken "not very well" |
| Arabic_Perc | Percent Arabic-speaking households where English is spoken "not very well" |
| OtherLang_Perc | Percent other language-speaking households where English is spoken "not very well" |
| Num_of_blocks | Number of blocks used to estimate total population and averages of demographic variables; only included in output table from Summarize Demographics tool |

### Feedback

Please fill out this [survey](https://forms.gle/c6PiRo5QfR6wQDEE9) to let me know how the tool worked for you!
