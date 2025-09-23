# Purpose: code for generating summaries for demographic analyses
# Author: Megan Kung
# Last edited: 9-18-2025

import arcpy
arcpy.env.overwriteOutput = True

analysis_boundaries = arcpy.GetParameterAsText(0)
analysis_id = arcpy.GetParameterAsText(1)
exportfile = arcpy.GetParameterAsText(2)

#CREATE NEW ID VARIABLE CALLED NEWID
#add field
arcpy.management.AddField(
    in_table=analysis_boundaries,
    field_name="new_id",
    field_type="BIGINTEGER",
    field_precision=None,
    field_scale=None,
    field_length=None,
    field_alias="",
    field_is_nullable="NULLABLE",
    field_is_required="NON_REQUIRED",
    field_domain=""
)

#generate sequential integer ids
arcpy.management.CalculateField(
    in_table=analysis_boundaries,
    field="new_id",
    expression="SequentialNumber()",
    expression_type="PYTHON3",
    code_block="""# Calculates a sequential number
# More calculator examples at esriurl.com/CalculatorExamples
rec=0
def SequentialNumber():
    global rec
    pStart = 1
    pInterval = 1
    if (rec == 0):
        rec = pStart
    else:
        rec = rec + pInterval
    return rec""",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS"
)


fields= ["new_id", analysis_id]
row_count = int(arcpy.GetCount_management(analysis_boundaries).getOutput(0))
iterations = row_count+1


#Select areas to analyze, iterate over each area
with arcpy.da.SearchCursor(analysis_boundaries, fields) as cursor:
  for i, row in zip(range(1,iterations), cursor):

    where_clause = 'new_id = {}'.format(row[0])
    
    # Select the current polygon
    arcpy.SelectLayerByAttribute_management(analysis_boundaries, "NEW_SELECTION", where_clause)
    
    #select the affected area by block centroids
    arcpy.management.SelectLayerByLocation(
        in_layer="Demographic_analysis_layer_2023",
        overlap_type="HAVE_THEIR_CENTER_IN",
        select_features= analysis_boundaries,
        search_distance=None,
        selection_type="NEW_SELECTION",
        invert_spatial_relationship="NOT_INVERT"
        )
        
            
    #Union
    arcpy.analysis.Union(
        in_features="Demographic_analysis_layer_2023 #;" + analysis_boundaries + " #",
        out_feature_class= arcpy.env.workspace + "/" + "CA_demographic_ana_Union" + str(i),
        join_attributes="ALL",
        )
        
    #selection of resulting union feature that has GEOID_block value, because union is including parts that don't have centroids within boundary layer
    arcpy.SelectLayerByAttribute_management("CA_demographic_ana_Union" + str(i), "NEW_SELECTION", "GEOID_block <>''")
            
    
#and then dissolve by block id
    arcpy.management.Dissolve(
        in_features="CA_demographic_ana_Union"+ str(i) ,
        out_feature_class=arcpy.env.workspace + "/" + "CA_demographic_ana_Dissolve"+ str(i),
        dissolve_field="GEOID_block",
        statistics_fields=None,
        multi_part="MULTI_PART",
        unsplit_lines="DISSOLVE_LINES",
        concatenation_separator=""
    )
    
#and then spatial join to put unioned layer back with dissolved layer
    arcpy.analysis.SpatialJoin(
        target_features="CA_demographic_ana_Dissolve" + str(i),
        join_features="CA_demographic_ana_Union" + str(i) ,
        out_feature_class=arcpy.env.workspace + "/" + "CA_demographic_SpatialJoin" + str(i),
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_COMMON",
        field_mapping='GEOID_block "GEOID_block" true true false 16 Text 0 0,First,#,CA_demographic_ana_Dissolve1,GEOID_block,0,15;P0010001 "Total Population" true true false 4 Long 0 0,First,#,CA_demographic_ana_Union1clean,P0010001,-1,-1;AIANHH "American Indian Area/Alaska Native Area/Hawaiian Home Land (Census)" true true false 4 Text 0 0,First,#,CA_demographic_ana_Union1clean,AIANHH,0,3;AIHHTLI "American Indian Trust Land/Hawaiian Home Land Indicator" true true false 1 Text 0 0,First,#,CA_demographic_ana_Union1clean,AIHHTLI,0,254;AIANHHFP "American Indian Area/Alaska Native Area/Hawaiian Home Land (FIPS)" true true false 5 Text 0 0,First,#,CA_demographic_ana_Union1clean,AIANHHFP,0,4;AIANHHCC "FIPS American Indian Area/Alaska Native Area/Hawaiian Home Land Class Code" true true false 2 Text 0 0,First,#,CA_demographic_ana_Union1clean,AIANHHCC,0,1;AIANHHNS "American Indian Area/Alaska Native Area/Hawaiian Home Land (NS)" true true false 8 Text 0 0,First,#,CA_demographic_ana_Union1clean,AIANHHNS,0,7;AITS "American Indian Tribal Subdivision (Census)" true true false 3 Text 0 0,First,#,CA_demographic_ana_Union1clean,AITS,0,2;AITSFP "American Indian Tribal Subdivision (FIPS)" true true false 5 Text 0 0,First,#,CA_demographic_ana_Union1clean,AITSFP,0,4;AITSCC "FIPS American Indian Tribal Subdivision Class Code" true true false 2 Text 0 0,First,#,CA_demographic_ana_Union1clean,AITSCC,0,1;AITSNS "American Indian Tribal Subdivision (NS)" true true false 8 Text 0 0,First,#,CA_demographic_ana_Union1clean,AITSNS,0,7;TTRACT "Tribal Census Tract" true true false 6 Text 0 0,First,#,CA_demographic_ana_Union1clean,TTRACT,0,5;TBLKGRP "Tribal Block Group" true true false 1 Text 0 0,First,#,CA_demographic_ana_Union1clean,TBLKGRP,0,254;GEOID_bg_20 "GEOID_bg_20" true true false 12 Text 0 0,First,#,CA_demographic_ana_Union1clean,GEOID_bg_20,0,11;FREQUENCY "FREQUENCY" true true false 4 Long 0 0,First,#,CA_demographic_ana_Union1clean,FREQUENCY,-1,-1;SUM_P0010001 "SUM_P0010001" true true false 8 Double 0 0,First,#,CA_demographic_ana_Union1clean,SUM_P0010001,-1,-1;GEOID_tract "GEOID_tract" true true false 11 Text 0 0,First,#,CA_demographic_ana_Union1clean,GEOID_tract,0,10;County_1 "County" true true false 255 Text 0 0,First,#,CA_demographic_ana_Union1clean,County_1,0,254;DAC_status "DAC_status" true true false 8000 Text 0 0,First,#,CA_demographic_ana_Union1clean,DAC_status,0,7999;MHI23 "MHI23" true true false 4 Long 0 0,First,#,CA_demographic_ana_Union1clean,MHI23,-1,-1;Pop_Total "Pop_Total" true true false 4 Long 0 0,First,#,CA_demographic_ana_Union1clean,Pop_Total,-1,-1;White "White" true true false 4 Long 0 0,First,#,CA_demographic_ana_Union1clean,White,-1,-1;Black "Black" true true false 4 Long 0 0,First,#,CA_demographic_ana_Union1clean,Black,-1,-1;AmerInd "AmerInd" true true false 4 Long 0 0,First,#,CA_demographic_ana_Union1clean,AmerInd,-1,-1;Asian "Asian" true true false 4 Long 0 0,First,#,CA_demographic_ana_Union1clean,Asian,-1,-1;PacIsl "PacIsl" true true false 4 Long 0 0,First,#,CA_demographic_ana_Union1clean,PacIsl,-1,-1;Other "Other" true true false 4 Long 0 0,First,#,CA_demographic_ana_Union1clean,Other,-1,-1;Mixed "Mixed" true true false 4 Long 0 0,First,#,CA_demographic_ana_Union1clean,Mixed,-1,-1;Hisp "Hisp" true true false 4 Long 0 0,First,#,CA_demographic_ana_Union1clean,Hisp,-1,-1;White_Perc "White_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,White_Perc,-1,-1;Black_Perc "Black_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,Black_Perc,-1,-1;AmerInd_Perc "AmerInd_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,AmerInd_Perc,-1,-1;Asian_Perc "Asian_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,Asian_Perc,-1,-1;PacIsl_Perc "PacIsl_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,PacIsl_Perc,-1,-1;Other_Perc "Other_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,Other_Perc,-1,-1;Mixed_Perc "Mixed_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,Mixed_Perc,-1,-1;Hisp_Perc "Hisp_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,Hisp_Perc,-1,-1;English_only_Perc "English_only_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,English_only_Perc,-1,-1;Spanish_Perc "Spanish_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,Spanish_Perc,-1,-1;French_Haitian_Cajun_Perc "French_Haitian_Cajun_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,French_Haitian_Cajun_Perc,-1,-1;German_WestGermanic_Perc "German_WestGermanic_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,German_WestGermanic_Perc,-1,-1;Russian_Polish_Slavic_Perc "Russian_Polish_Slavic_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,Russian_Polish_Slavic_Perc,-1,-1;OtherIndoEuro_Perc "OtherIndoEuro_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,OtherIndoEuro_Perc,-1,-1;Korean_Perc "Korean_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,Korean_Perc,-1,-1;Chinese_Perc "Chinese_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,Chinese_Perc,-1,-1;Vietnamese_Perc "Vietnamese_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,Vietnamese_Perc,-1,-1;Tagalog_incl_Filipino_Perc "Tagalog_incl_Filipino_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,Tagalog_incl_Filipino_Perc,-1,-1;OtherAsianPacIsl_Perc "OtherAsianPacIsl_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,OtherAsianPacIsl_Perc,-1,-1;Arabic_Perc "Arabic_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,Arabic_Perc,-1,-1;OtherLang_Perc "OtherLang_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,OtherLang_Perc,-1,-1;LEP_Perc "LEP_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,LEP_Perc,-1,-1;LEP_Spanish_Perc "LEP_Spanish_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,LEP_Spanish_Perc,-1,-1;LEP_French_Haitian_Cajun_Perc "LEP_French_Haitian_Cajun_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,LEP_French_Haitian_Cajun_Perc,-1,-1;LEP_German_WestGermanic_Perc "LEP_German_WestGermanic_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,LEP_German_WestGermanic_Perc,-1,-1;LEP_Russian_Polish_Slavic_Perc "LEP_Russian_Polish_Slavic_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,LEP_Russian_Polish_Slavic_Perc,-1,-1;LEP_OtherIndoEuro_Perc "LEP_OtherIndoEuro_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,LEP_OtherIndoEuro_Perc,-1,-1;LEP_Korean_Perc "LEP_Korean_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,LEP_Korean_Perc,-1,-1;LEP_Chinese_Perc "LEP_Chinese_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,LEP_Chinese_Perc,-1,-1;LEP_Vietnamese_Perc "LEP_Vietnamese_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,LEP_Vietnamese_Perc,-1,-1;LEP_Tagalog_incl_Filipino_Perc "LEP_Tagalog_incl_Filipino_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,LEP_Tagalog_incl_Filipino_Perc,-1,-1;LEP_OtherAsianPacIsl_Perc "LEP_OtherAsianPacIsl_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,LEP_OtherAsianPacIsl_Perc,-1,-1;LEP_Arabic_Perc "LEP_Arabic_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,LEP_Arabic_Perc,-1,-1;LEP_OtherLang_Perc "LEP_OtherLang_Perc" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,LEP_OtherLang_Perc,-1,-1;Perc_BG_Pop "Perc_BG_Pop" true true false 4 Float 0 0,First,#,CA_demographic_ana_Union1clean,Perc_BG_Pop,-1,-1', 
        match_option="CONTAINS",
        search_radius=None,
        distance_field_name="",
        match_fields=None
    )
    
    #some of the analysis_id vars end up blank, need to fill those in
    #calculate fields
    arcpy.management.CalculateField(
        in_table="CA_demographic_SpatialJoin" + str(i),
        field= analysis_id,
        expression= '"{}"'.format(row[1]),
        expression_type="PYTHON3",
        code_block="",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS"
        )        
    arcpy.management.CalculateField(
        in_table="CA_demographic_SpatialJoin" + str(i),
        field= "new_id",
        expression= '"{}"'.format(row[0]),
        expression_type="PYTHON3",
        code_block="",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS"
        )


#get all the tables from the individual features into one table, then can do calculations all at once
for i in range(1,iterations):
    arcpy.management.MakeTableView("CA_demographic_SpatialJoin"+str(i), "CA_demographic_SpatialJoin" + str(i) + "_table")

    # Persist the view to a table
    arcpy.management.CopyRows("CA_demographic_SpatialJoin" + str(i) + "_table", arcpy.env.workspace + "/" + "Analysis_table" + str(i))

for i in (range(2,iterations)):
    arcpy.Append_management("Analysis_table" + str(i), "Analysis_table1", "TEST", "", "")
    
#ok! let's calculate on the new appended table!

vars = ["MHI23", "White_Perc", "Black_Perc", "AmerInd_Perc", "Asian_Perc", "PacIsl_Perc", "Other_Perc", "Mixed_Perc", "Hisp_Perc",
"English_Only_Perc", "Spanish_Perc", "French_Haitian_Cajun_Perc", "German_WestGermanic_Perc", "Russian_Polish_Slavic_Perc", "OtherIndoEuro_Perc","Korean_Perc", "Chinese_Perc", "Vietnamese_Perc", "Tagalog_incl_Filipino_Perc", "OtherAsianPacIsl_Perc", "Arabic_Perc", "OtherLang_Perc", "LEP_Perc","LEP_Spanish_Perc", "LEP_French_Haitian_Cajun_Perc", "LEP_German_WestGermanic_Perc", "LEP_Russian_Polish_Slavic_Perc", "LEP_OtherIndoEuro_Perc","LEP_Korean_Perc", "LEP_Chinese_Perc", "LEP_Vietnamese_Perc", "LEP_Tagalog_incl_Filipino_Perc", "LEP_OtherAsianPacIsl_Perc", "LEP_Arabic_Perc", "LEP_OtherLang_Perc"]

    #add variable for numerator
for v in vars:
    arcpy.management.AddField(
    in_table="Analysis_table1",
    field_name= v + "_weight_num",
    field_type="DOUBLE",
    field_precision=None,
    field_scale=None,
    field_length=4,
    field_alias="",
    field_is_nullable="NULLABLE",
    field_is_required="NON_REQUIRED",
    field_domain=""
    )


#calculate numerator 
num_calc = ["!Perc_BG_Pop! * !Pop_Total! *!MHI23!",
            "!Perc_BG_Pop! * !Pop_Total! *!White_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!Black_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!AmerInd_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!Asian_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!PacIsl_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!Other_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!Mixed_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!Hisp_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!English_Only_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!Spanish_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!French_Haitian_Cajun_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!German_WestGermanic_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!Russian_Polish_Slavic_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!OtherIndoEuro_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!Korean_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!Chinese_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!Vietnamese_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!Tagalog_incl_Filipino_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!OtherAsianPacIsl_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!Arabic_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!OtherLang_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!LEP_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!LEP_Spanish_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!LEP_French_Haitian_Cajun_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!LEP_German_WestGermanic_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!LEP_Russian_Polish_Slavic_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!LEP_OtherIndoEuro_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!LEP_Korean_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!LEP_Chinese_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!LEP_Vietnamese_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!LEP_Tagalog_incl_Filipino_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!LEP_OtherAsianPacIsl_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!LEP_Arabic_Perc!",
            "!Perc_BG_Pop! * !Pop_Total! *!LEP_OtherLang_Perc!"]
for v, nc in zip(vars, num_calc):
    arcpy.management.CalculateField(
        in_table="Analysis_table1",
        field= v + "_weight_num",
        expression= nc,
        expression_type="PYTHON3",
        code_block="",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS")

#add variable for denominator
arcpy.management.AddField(
    in_table="Analysis_table1",
    field_name="Weight_den",
    field_type="DOUBLE",
    field_precision=None,
    field_scale=None,
    field_length=4,
    field_alias="",
    field_is_nullable="NULLABLE",
    field_is_required="NON_REQUIRED",
    field_domain=""
)

arcpy.management.CalculateField(
    in_table="Analysis_table1",
    field= "Weight_den",
    expression= "!Perc_BG_Pop! * !Pop_Total!",
    expression_type="PYTHON3",
    code_block="",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS"
)


#then sum denominator according to analysis boundaries
arcpy.analysis.Statistics(
    in_table="Analysis_table1",
    out_table=arcpy.env.workspace + "/" + "Weight_den",
    statistics_fields="Weight_den SUM",
    case_field=analysis_id,
    concatenation_separator=""
)

#then join denominator sum table back to CA_demographic_ana_Union" + str(i)
arcpy.management.JoinField(
    in_data="Analysis_table1",
    in_field= analysis_id,
    join_table= "Weight_den",
    join_field=analysis_id,
    fields=None,
    fm_option="NOT_USE_FM",
    field_mapping=None,
    index_join_fields="NO_INDEXES"
)


#then sum numerator according to analysis boundaries
for v in vars:
    arcpy.analysis.Statistics(
    in_table="Analysis_table1",
    out_table=arcpy.env.workspace + "/" + v + "_num_sum",
    statistics_fields= v + "_weight_num SUM",
    case_field= analysis_id,
    concatenation_separator=""
    )


#then join numerator sum table back to CA_demographic_ana_Union" 
for v in vars:
    arcpy.management.JoinField(
    in_data="Analysis_table1",
    in_field=analysis_id,
    join_table= v + "_num_sum",
    join_field= analysis_id,
    fields=None,
    fm_option="NOT_USE_FM",
    field_mapping=None,
    index_join_fields="NO_INDEXES"
    )

#then add field to divide summed numerator by denominator
for v in vars:
    arcpy.management.AddField(
    in_table="Analysis_table1",
    field_name=v + "_div",
    field_type="DOUBLE",
    field_precision=None,
    field_scale=None,
    field_length=4,
    field_alias="",
    field_is_nullable="NULLABLE",
    field_is_required="NON_REQUIRED",
    field_domain=""
    )

#calculate
div_calc = ["!SUM_MHI23_weight_num!/!Sum_Weight_den!",
            "!SUM_White_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Black_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_AmerInd_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Asian_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_PacIsl_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Other_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Mixed_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Hisp_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_English_Only_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Spanish_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_French_Haitian_Cajun_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_German_WestGermanic_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Russian_Polish_Slavic_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_OtherIndoEuro_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Korean_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Chinese_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Vietnamese_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Tagalog_incl_Filipino_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_OtherAsianPacIsl_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Arabic_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_OtherLang_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_LEP_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_LEP_Spanish_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_LEP_French_Haitian_Cajun_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_LEP_German_WestGermanic_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_LEP_Russian_Polish_Slavic_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_LEP_OtherIndoEuro_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_LEP_Korean_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_LEP_Chinese_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_LEP_Vietnamese_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_LEP_Tagalog_incl_Filipino_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_LEP_OtherAsianPacIsl_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_LEP_Arabic_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_LEP_OtherLang_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_White_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Black_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_AmerInd_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Asian_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_PacIsl_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Other_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Mixed_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Hisp_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_English_Only_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Spanish_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_French_Haitian_Cajun_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_German_WestGermanic_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Russian_Polish_Slavic_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_OtherIndoEuro_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Korean_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Chinese_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Vietnamese_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Tagalog_incl_Filipino_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_OtherAsianPacIsl_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_Arabic_Perc_weight_num!/!Sum_Weight_den!",
            "!SUM_OtherLang_Perc_weight_num!/!Sum_Weight_den!"]
for v, dc in zip(vars, div_calc):
    arcpy.management.CalculateField(
    in_table="Analysis_table1",
    field= v + "_div",
    expression= dc,
    expression_type="PYTHON3",
    code_block="",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS"
    )


#and then use Statistics tool to calculate average of weighted values
arcpy.analysis.Statistics(
    in_table="Analysis_table1",
    out_table=arcpy.env.workspace + "/" + "Summarized_Demographic_Stats",
    statistics_fields="SUM_Weight_den MEAN;MHI23_div MEAN;White_Perc_div MEAN;Black_Perc_div MEAN;AmerInd_Perc_div MEAN;Asian_Perc_div MEAN;PacIsl_Perc_div MEAN;Other_Perc_div MEAN;Mixed_Perc_div MEAN;Hisp_Perc_div MEAN;English_Only_Perc_div MEAN;Spanish_Perc_div MEAN;French_Haitian_Cajun_Perc_div MEAN;German_WestGermanic_Perc_div MEAN;Russian_Polish_Slavic_Perc_div MEAN;OtherIndoEuro_Perc_div MEAN;Korean_Perc_div MEAN;Chinese_Perc_div MEAN;Vietnamese_Perc_div MEAN;Tagalog_incl_Filipino_Perc_div MEAN;OtherAsianPacIsl_Perc_div MEAN;Arabic_Perc_div MEAN;OtherLang_Perc_div MEAN;LEP_Perc_div MEAN;LEP_Spanish_Perc_div MEAN;LEP_French_Haitian_Cajun_Perc_div MEAN;LEP_German_WestGermanic_Perc_div MEAN;LEP_Russian_Polish_Slavic_Perc_div MEAN;LEP_OtherIndoEuro_Perc_div MEAN;LEP_Korean_Perc_div MEAN;LEP_Chinese_Perc_div MEAN;LEP_Vietnamese_Perc_div MEAN;LEP_Tagalog_incl_Filipino_Perc_div MEAN;LEP_OtherAsianPacIsl_Perc_div MEAN;LEP_Arabic_Perc_div MEAN;LEP_OtherLang_Perc_div MEAN",
    case_field= analysis_id,
    concatenation_separator=""
)

    #rename variables
arcpy.AlterField_management("Summarized_Demographic_Stats", "FREQUENCY", "Num_of_blocks", "Num_of_blocks")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_SUM_Weight_den", "TotalPop", "TotalPop")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_MHI23_div", "MHI23", "MHI23")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_Hisp_Perc_div", "Hisp_Perc", "Hisp_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_White_Perc_div", "White_Perc", "White_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_Asian_Perc_div", "Asian_Perc", "Asian_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_Black_Perc_div", "Black_Perc", "Black_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_AmerInd_Perc_div", "AmerInd_Perc", "AmerInd_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_PacIsl_Perc_div", "PacIsl_Perc", "PacIsl_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_Mixed_Perc_div", "Mixed_Perc", "Mixed_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_Other_Perc_div", "Other_Perc", "Other_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_English_Only_Perc_div", "English_Only_Perc", "English_Only_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_Spanish_Perc_div", "Spanish_Perc", "Spanish_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_French_Haitian_Cajun_Perc_div", "French_Haitian_Cajun_Perc", "French_Haitian_Cajun_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_German_WestGermanic_Perc_div", "German_WestGermanic_Perc", "German_WestGermanic_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_Russian_Polish_Slavic_Perc_div", "Russian_Polish_Slavic_Perc", "Russian_Polish_Slavic_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_OtherIndoEuro_Perc_div", "OtherIndoEuro_Perc", "OtherIndoEuro_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_Korean_Perc_div", "Korean_Perc", "Korean_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_Chinese_Perc_div", "Chinese_Perc", "Chinese_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_Vietnamese_Perc_div", "Vietnamese_Perc", "Vietnamese_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_Tagalog_incl_Filipino_Perc_div", "Tagalog_incl_Filipino_Perc", "Tagalog_incl_Filipino_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_OtherAsianPacIsl_Perc_div", "OtherAsianPacIsl_Perc", "OtherAsianPacIsl_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_Arabic_Perc_div", "Arabic_Perc", "Arabic_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_OtherLang_Perc_div", "OtherLang_Perc", "OtherLang_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_LEP_Perc_div", "LEP_Perc", "LEP_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_LEP_Spanish_Perc_div", "LEP_Spanish_Perc", "LEP_Spanish_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_LEP_French_Haitian_Cajun_Perc_div", "LEP_French_Haitian_Cajun_Perc", "LEP_French_Haitian_Cajun_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_LEP_German_WestGermanic_Perc_div", "LEP_German_WestGermanic_Perc", "LEP_German_WestGermanic_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_LEP_Russian_Polish_Slavic_Perc_div", "LEP_Russian_Polish_Slavic_Perc", "LEP_Russian_Polish_Slavic_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_LEP_OtherIndoEuro_Perc_div", "LEP_OtherIndoEuro_Perc", "LEP_OtherIndoEuro_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_LEP_Korean_Perc_div", "LEP_Korean_Perc", "LEP_Korean_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_LEP_Chinese_Perc_div", "LEP_Chinese_Perc", "LEP_Chinese_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_LEP_Vietnamese_Perc_div", "LEP_Vietnamese_Perc", "LEP_Vietnamese_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_LEP_Tagalog_incl_Filipino_Perc_div", "LEP_Tagalog_incl_Filipino_Perc", "LEP_Tagalog_incl_Filipino_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_LEP_OtherAsianPacIsl_Perc_div", "LEP_OtherAsianPacIsl_Perc", "LEP_OtherAsianPacIsl_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_LEP_Arabic_Perc_div", "LEP_Arabic_Perc", "LEP_Arabic_Perc")
arcpy.AlterField_management("Summarized_Demographic_Stats", "MEAN_LEP_OtherLang_Perc_div", "LEP_OtherLang_Perc", "LEP_OtherLang_Perc")


#export to excel
arcpy.conversion.TableToExcel(
    Input_Table="Summarized_Demographic_Stats",
    Output_Excel_File= exportfile,
    Use_field_alias_as_column_header="NAME",
    Use_domain_and_subtype_description="CODE"
)


#delete intermediate tables
for table in arcpy.ListTables():
    if table[-7:] == "num_sum" or table == "Weight_den" or table[0:14]=="Analysis_table":
 #       print ("Deleting intermediate file:  {}".format(table))
        arcpy.Delete_management(table)


intermFeatures = ["CA_demographic_ana_Dissolve", "CA_demographic_ana_Union","CA_demographic_SpatialJoin"] 
for interm in intermFeatures:
    for i in range(1,iterations):
 #       print("Deleting intermediate file:" + interm + str(i))
        arcpy.Delete_management(arcpy.env.workspace + "/" + interm + str(i))
    

#delete new_id
arcpy.management.DeleteField(
    in_table=analysis_boundaries,
    drop_field="new_id",
    method="DELETE_FIELDS"
)