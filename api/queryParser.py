import json
from collections import defaultdict

def extractClauseData(jsonData) -> dict:
    clauseDict = {}
    selectDict = defaultdict(list)
    fromDict = defaultdict(list)
    whereDict = defaultdict(list)
    groupDict = defaultdict(list)
    havingDict = defaultdict(list)
    distinctFlag = False

    formattedData = json.loads(jsonData)
    selectStatement = formattedData['stmts'][0]['stmt']['SelectStmt']
    skipList = ["location", "relpersistence", "inh", "kind"]

    for clause in selectStatement:
        # Select Clause
        if "targetList" in clause:
            for resTarget in selectStatement["targetList"]:
                for field, value in traverseJson(resTarget):
                    curIndex = len(field) - 1
                    if field[curIndex] not in skipList:
                        # Assign column and possible alias
                        if field[4] == 0:
                            selectDict["targets"].append([str(value), ""])
                        elif field[4] == 1:
                            selectDict["targets"][-1] = [selectDict["targets"][-1][0], str(value)]
                        # "Value" selected
                        else:
                            selectDict["targets"].append(["VALUE", str(value)])
        # From Clause
        elif "fromClause" in clause:
            for rangeVar in selectStatement["fromClause"]:
                for field, value in traverseJson(rangeVar):
                    curIndex = len(field) - 1
                    if field[curIndex] not in skipList:
                        if field[curIndex] == "relname":
                            fromDict[field[curIndex]].append(["", str(value)])
                        elif field[curIndex] == "aliasname" and fromDict["relname"][-1][0] == "":
                            fromDict["relname"][-1] = [value, fromDict["relname"][-1][1]]
                        elif field[curIndex] == "jointype":
                            fromDict[field[curIndex]].append(str(value))
                        else:
                            if not value.isalnum():
                                fromDict["joinvalue"].append([str(value)])
                            else:
                                fromDict["joinvalue"][-1].append(str(value))
            for i in range(len(fromDict["jointype"])):
                fromDict["joinvalue"][-1 - i].append(fromDict["jointype"][i])
            fromDict.pop("jointype", None)
        # Where Clause
        elif "whereClause" in clause:
            leftColChecked = False
            rightColChecked = False
            if "BoolExpr" in selectStatement["whereClause"]:
                for field, value in traverseJson(selectStatement["whereClause"]["BoolExpr"]["args"]):
                    curIndex = len(field) - 1
                    if field[curIndex] not in skipList:
                        if field[2] == "name":
                            whereDict["conditions"].append(str(value))
                        elif field[2] == "lexpr":
                            rightColChecked = False
                            if not leftColChecked:
                                leftColChecked = True
                                whereDict["conditions"][-1] = [whereDict["conditions"][-1], "", str(value)]
                            else:
                                leftColChecked = False
                                whereDict["conditions"][-1] = [whereDict["conditions"][-1][0], whereDict["conditions"][-1][2], str(value)]
                        elif field[2] == "rexpr":
                            leftColChecked = False
                            if not rightColChecked:
                                rightColChecked = True
                                whereDict["conditions"][-1] = [whereDict["conditions"][-1][0], whereDict["conditions"][-1][1], whereDict["conditions"][-1][2], "", str(value)]
                            else:
                                rightColChecked = False
                                whereDict["conditions"][-1] = [whereDict["conditions"][-1][0], whereDict["conditions"][-1][1], whereDict["conditions"][-1][2], whereDict["conditions"][-1][4], str(value)]
            else:
                for field, value in traverseJson(selectStatement["whereClause"]):
                    curIndex = len(field) - 1
                    if field[curIndex] not in skipList:
                        if field[1] == "name":
                            whereDict["conditions"].append(str(value))
                        elif field[1] == "lexpr":
                            rightColChecked = False
                            if not leftColChecked:
                                leftColChecked = True
                                whereDict["conditions"][-1] = [whereDict["conditions"][-1], "", str(value)]
                            else:
                                leftColChecked = False
                                whereDict["conditions"][-1] = [whereDict["conditions"][-1][0], whereDict["conditions"][-1][2], str(value)]
                        elif field[1] == "rexpr":
                            leftColChecked = False
                            if not rightColChecked:
                                rightColChecked = True
                                whereDict["conditions"][-1] = [whereDict["conditions"][-1][0], whereDict["conditions"][-1][1], whereDict["conditions"][-1][2], "", str(value)]
                            else:
                                rightColChecked = False
                                whereDict["conditions"][-1] = [whereDict["conditions"][-1][0], whereDict["conditions"][-1][1], whereDict["conditions"][-1][2], whereDict["conditions"][-1][4], str(value)]
        # Group By Clause
        elif "groupClause" in clause:
            hasAlias = False
            for field, value in traverseJson(selectStatement["groupClause"]):
                curIndex = len(field) - 1
                if field[curIndex] not in skipList:
                    if value in (x[0] for x in fromDict["relname"]):
                        hasAlias = True
                        groupDict["groups"].append((str(value)))
                    elif hasAlias:
                        hasAlias = False
                        groupDict["groups"][-1] = [groupDict["groups"][-1], str(value)]
                    else:
                        groupDict["groups"].append(["", str(value)])
        # Having Clause
        elif "havingClause" in clause:
            leftColChecked = False
            rightColChecked = False
            if "BoolExpr" in selectStatement["havingClause"]:
                for field, value in traverseJson(selectStatement["havingClause"]["BoolExpr"]["args"]):
                    curIndex = len(field) - 1
                    if field[curIndex] not in skipList:
                        if field[2] == "name":
                            havingDict["conditions"].append(str(value))
                        elif field[2] == "lexpr":
                            rightColChecked = False
                            if not leftColChecked:
                                leftColChecked = True
                                havingDict["conditions"][-1] = [havingDict["conditions"][-1], "", str(value)]
                            else:
                                leftColChecked = False
                                havingDict["conditions"][-1] = [havingDict["conditions"][-1][0], havingDict["conditions"][-1][2], str(value)]
                        elif field[2] == "rexpr":
                            leftColChecked = False
                            if not rightColChecked:
                                rightColChecked = True
                                havingDict["conditions"][-1] = [havingDict["conditions"][-1][0], havingDict["conditions"][-1][1], havingDict["conditions"][-1][2], "", str(value)]
                            else:
                                rightColChecked = False
                                havingDict["conditions"][-1] = [havingDict["conditions"][-1][0], havingDict["conditions"][-1][1], havingDict["conditions"][-1][2], havingDict["conditions"][-1][4], str(value)]
            else:
                for field, value in traverseJson(selectStatement["havingClause"]):
                    curIndex = len(field) - 1
                    if field[curIndex] not in skipList:
                        if field[1] == "name":
                            havingDict["conditions"].append(str(value))
                        elif field[1] == "lexpr":
                            rightColChecked = False
                            if not leftColChecked:
                                leftColChecked = True
                                havingDict["conditions"][-1] = [havingDict["conditions"][-1], "", str(value)]
                            else:
                                leftColChecked = False
                                havingDict["conditions"][-1] = [havingDict["conditions"][-1][0], havingDict["conditions"][-1][2], str(value)]
                        elif field[1] == "rexpr":
                            leftColChecked = False
                            if not rightColChecked:
                                rightColChecked = True
                                havingDict["conditions"][-1] = [havingDict["conditions"][-1][0], havingDict["conditions"][-1][1], havingDict["conditions"][-1][2], "", str(value)]
                            else:
                                rightColChecked = False
                                havingDict["conditions"][-1] = [havingDict["conditions"][-1][0], havingDict["conditions"][-1][1], havingDict["conditions"][-1][2], havingDict["conditions"][-1][4], str(value)]
        # Limit Clause
        elif "limitCount" in clause:
            limitNum = selectStatement["limitCount"]["A_Const"]["val"]["Integer"]["ival"]
        elif "limitOption" in clause:
            if selectStatement["limitOption"] == "LIMIT_OPTION_COUNT":
                clauseDict["Limit"] = "Limited to {} results".format(limitNum)
            else:
                clauseDict["Limit"] = "Unlimited results"
        # Distinct Flag
        elif "distinctClause" in clause:
            distinctFlag = True

    # Combine the dictionaries
    clauseDict["Select"] = selectDict
    clauseDict["From"] = fromDict
    clauseDict["Where"] = whereDict
    clauseDict["Group"] = groupDict
    clauseDict["Having"] = havingDict
    clauseDict["Distinct"] = distinctFlag

    return clauseDict

def traverseJson(obj, keys=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from traverseJson(v, keys + (k,))
    elif any(isinstance(obj, t) for t in (list, tuple)):
        for idx, item in enumerate(obj):
            yield from traverseJson(item, keys + (idx,))
    else:
        yield keys, obj