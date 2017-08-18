import json, datetime, re


class ReportHTML:

    __reportFile = None
    __charset = 'utf-8'
    __title = 'Report'
    __title_rows = 0

    def __init__( self, fileName, charset='utf-8', title='' ):
        self.__charset = charset
        self.__reportFile = open(fileName, "w")
        self.__title = title

    def printHTMLRaw(self, text):
        self.__reportFile.write(text)

    def printHTMLHead(self, title="Report"):
        html_text = '<html>\n<head>\n<title>' + self.__title + '</title>\n'\
            '</head>\n<body>\n'
        self.__reportFile.write(html_text)

    def printHTMLTail(self, title="Report"):
        html_text = '</body>\n</html>'
        self.__reportFile.write(html_text)

    def printHTMLHeader(self):
        html_text = '<center><h1>' + self.__title + '</h1></center><br/>'
        self.__reportFile.write(html_text)

    def printNewTable(self, columnTitles ):
        html_text = '<table>\n<tr>\n'
        self.__title_rows = len(columnTitles)
        for col_title in columnTitles:
            html_text += "<th>" + col_title + "</th>"
        html_text += '</tr>'
        self.__reportFile.write(html_text)

    def printNewTableRow(self, dataSet):
        if len(dataSet) < self.__title_rows:
            dataSet.extend(
                ["" for i in range(0,self.__title_rows - len(dataSet))] )
        elif len(dataSet) > self.__title_rows:
            while ( len(dataSet) > self.__title_rows ):
                dataSet[self.__title_rows-1] += " " + dataSet.pop( self.__title_rows )
        html_text = "<tr>"
        for data in dataSet:
            html_text+="<td>" + str(data) + "</td>"
        html_text += "</tr>"
        self.__reportFile.write(html_text)


# Main

# JSON config reading
config = None
try:
    with open('config.json', 'r') as file:
        config = json.load(file)
except json.decoder.JSONDecodeError as error:
    print("Your config is wrong at line " + str(error.lineno) + "\n")
    print("The parser wants: " + str(error.msg))

charcolumns = int(config["parse"]["charcolumns"])
conflictcol = int(config["parse"]["conflictcol"])

# Preparing regex for remaining columns
#~remainCols = len(config["parse"]["columns"]) - charcolumns
dataRegex = re.compile('\s*(\d*|-)\s+(\d*)\s+(.+)\s+(.+)$')

# Starting making the report
report = ReportHTML(config["outfile"], title='Subversion report at ' +
                    str(datetime.datetime.now()))
report.printHTMLHead()
report.printHTMLHeader()
report.printNewTable(config["parse"]["columns"].values())

svn_status = open(config["infile"], "r")

# Reading svn status file line by line, parsing and writing
# to the report table
j=0
for line in svn_status:
    dataRow = dict()

    # Don't forget that str indices start with 0
    for i in range(1,charcolumns+1):
        # If no svn fill with nothing
        if line[0] == '?' and i>1 :
            dataRow[i] = ""
            continue
        # Else parse as config said
        try:
            dataRow[i] = config["parse"]["data"][str(i)][line[i-1]]
        except KeyError:
            dataRow[i] = "Undefined condition"
            print("Your config doesn't consider this snv output")

    # If conflict exists, reading the next line
    if line[conflictcol-1] == 'C':
        confilctIssue = svn_status.readline()[charcolumns:].strip()
    else:
        confilctIssue = ""
    dataRow[conflictcol] = confilctIssue

    dataSet = list(dataRow.values())

    info = line[charcolumns:]
    dataRemains = dataRegex.match(info)
    if dataRemains:
        for data in dataRemains.groups():
            dataSet.append(data.strip())

    report.printNewTableRow(dataSet)

    j+=1
    print("Parsing line "+str(j)+"...\n")

report.printHTMLTail()

exit(0)