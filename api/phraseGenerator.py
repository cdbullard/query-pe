from collections import defaultdict

def extractPhrases(dict) -> str:
    relations = []
    selectValues = []
    tableColumns = defaultdict(list)
    matchedColumnsAndTables = defaultdict(list)

    for table in dict["From"]["relname"]:
        relations.append(table)
    
    for target in dict["Select"]["targets"]:
        curAlias = target[0]
        curColumn = target[1]
        tableColumns[curAlias].append(curColumn)

    if any("VALUE" in val for val in dict["Select"]["targets"]):
        for val in dict["Select"]["targets"]:
            if val[0] == "VALUE":
                selectValues.append(val[1])

    for table in tableColumns:
        for rel in relations:
            if rel[0] == table:
                matchedColumnsAndTables[rel[1]] = tableColumns[table]

    result = f"A total of {len(relations)} tables were used in this query.\n\n"
    tables = ""
    joins = ""
    conditions = ""
    conditionCount = 0
    groupings = ""
    groupCount = 0
    havings = ""
    havingCount = 0
    limits = ""

    if len(relations) == 1:
        result = result.replace("tables", "table")
        result = result.replace("were", "was")
    
    if len(matchedColumnsAndTables) > 0:
        for match in matchedColumnsAndTables:
            if (len(matchedColumnsAndTables[match]) > 1):
                tables += f"From the table '{match}', the following columns were returned in the result set: {', '.join(matchedColumnsAndTables[match])}.\n"
            else:
                tables += f"From the table '{match}', the following column was returned in the result set: {', '.join(matchedColumnsAndTables[match])}.\n"

    if selectValues:
        tables += f"The following values were included in the result set: {', '.join(selectValues)}.\n"

    if len(tables) > 0:
        result += tables + "\n"

    for join in dict["From"]["joinvalue"]:
        leftTable = ""
        rightTable = ""
        joinType = ""

        for table in matchedColumnsAndTables:
            if matchedColumnsAndTables[table] == tableColumns[join[1]] and leftTable == "":
                leftTable = table
            elif matchedColumnsAndTables[table] == tableColumns[join[3]] and rightTable == "":
                rightTable = table
            elif leftTable != "" and rightTable != "":
                break

        if (join[0] == "="):
            joinType = "equal to"
        elif (join[0] == ">"):
            joinType = "greater than"
        elif (join[0] == "<"):
            joinType = "less than"
        elif (join[0] == ">="):
            joinType = "greater than or equal to"
        elif (join[0] == "<="):
            joinType = "less than or equal to"
        elif (join[0] == "<>"):
            comparisonWhere = "does not equal"

        if join[2] == join[4] and join[0] == "=":
            joins += f"The table '{leftTable}' was joined with '{rightTable}' where '{join[2]}' from both tables are equal.\n"
        else:
            joins += f"The table '{leftTable}' was joined with '{rightTable}' where '{join[2]}' from '{leftTable}' is {joinType} '{join[4]}' from '{rightTable}'.\n"

    if len(joins) > 0:
        result += joins + "\n"

    for condition in dict["Where"]["conditions"]:
        conditionCount += 1
        leftArgWhere = ""
        rightArgWhere = ""
        comparisonWhere = ""
        leftTableFound = False
        rightTableFound = False

        for table in matchedColumnsAndTables:
            if matchedColumnsAndTables[table] == tableColumns[condition[1]]:
                leftArgWhere = table
                leftTableFound = True
            elif matchedColumnsAndTables[table] == tableColumns[condition[3]]:
                rightArgWhere = table
                rightTableFound = True
                break

        if (condition[0] == "="):
            comparisonWhere = "equal to"
        elif (condition[0] == ">"):
            comparisonWhere = "greater than"
        elif (condition[0] == "<"):
            comparisonWhere = "less than"
        elif (condition[0] == ">="):
            comparisonWhere = "greater than or equal to"
        elif (condition[0] == "<="):
            comparisonWhere = "less than or equal to"
        elif (condition[0] == "<>"):
            comparisonWhere = "does not equal"

        startPart = "A comparison was made to return records where "
        leftPart = f"the column '{condition[2]}' from table '{leftArgWhere}' is {comparisonWhere} " if leftTableFound else f"the value '{condition[2]}' is {comparisonWhere} "
        rightPart = f"the column '{condition[4]}' from table '{rightArgWhere}'. " if rightTableFound else f"the value '{condition[4]}'."

        conditions += startPart + leftPart + rightPart + "\n"

    if conditionCount > 0:
        result += conditions + "\n"

    for group in dict["Group"]["groups"]:
        groupCount += 1
        groupTable = ""

        for table in matchedColumnsAndTables:
            if matchedColumnsAndTables[table] == tableColumns[group[0]]:
                groupTable = table
                break
        
        groupings += f"'{group[1]}' from the table '{groupTable}', " if groupTable != "" else f"'{group[1]}', "

    if groupCount > 0:
        result += "Records were grouped together on the following "
        result += "columns: " if groupCount > 1 else "column: "
        result += groupings[:-2] + ".\n\n"
    
    for having in dict["Having"]["conditions"]:
        havingCount += 1
        leftArgHaving = ""
        rightArgHaving = ""
        comparisonHaving = ""
        leftTableFound = False
        rightTableFound = False

        for table in matchedColumnsAndTables:
            if matchedColumnsAndTables[table] == tableColumns[having[1]]:
                leftArgHaving = table
                leftTableFound = True
            elif matchedColumnsAndTables[table] == tableColumns[having[3]]:
                rightArgHaving = table
                rightTableFound = True
                break

        if (having[0] == "="):
            comparisonHaving = "equal to"
        elif (having[0] == ">"):
            comparisonHaving = "greater than"
        elif (having[0] == "<"):
            comparisonHaving = "less than"
        elif (having[0] == ">="):
            comparisonHaving = "greater than or equal to"
        elif (having[0] == "<="):
            comparisonHaving = "less than or equal to"
        elif (having[0] == "<>"):
            comparisonHaving = "does not equal"

        startPart = "A comparison was made to return records where "
        leftPart = f"the column '{having[2]}' from table '{leftArgHaving}' is {comparisonHaving} " if leftTableFound else f"the value '{having[2]}' is {comparisonHaving} "
        rightPart = f"the column '{having[4]}' from table '{rightArgHaving}'. " if rightTableFound else f"the value '{having[4]}'."

        havings += startPart + leftPart + rightPart + "\n"
    
    if havingCount > 0:
        result += havings + "\n"

    if "Limited to" in dict["Limit"]:
        limits += "The number of returned results was " + dict["Limit"].lower() + "."
    else:
        limits += "The number of returned results was unlimited."

    result += limits

    if dict["Distinct"]:
        result += " Only unique results were returned."
    
    return result