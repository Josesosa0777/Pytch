import os
import sqlite3
import stat

DATABASE_SELECT = 'SQLITE'  # Database selection values are : MYSQL, SQLITE
try:
    import mysql.connector
except:
    DATABASE_SELECT = 'SQLITE'  # Database selection values are : MYSQL, SQLITE


class DatabaseManagement:
    _singleton = None
    db_file_path = ""

    @staticmethod
    def get_instance():
        """ Static access method. """
        if DatabaseManagement._singleton is None:
            DatabaseManagement()
        return DatabaseManagement._singleton

    def __init__(self):
        self.connection = self.connect_to_db()

        if DatabaseManagement._singleton is None:
            DatabaseManagement._singleton = self

    def connect_to_db(self):
        """ create a database connection to the SQLite database
                specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        if DATABASE_SELECT == 'SQLITE':
            if not os.access(DatabaseManagement.db_file_path, os.W_OK):
                os.chmod(DatabaseManagement.db_file_path, stat.S_IWRITE)

            conn = sqlite3.connect(DatabaseManagement.db_file_path)
            conn.text_factory = str
        elif DATABASE_SELECT == 'MYSQL':
            conn = mysql.connector.connect(host='10.130.88.169',
                                           database='standardtemplates',
                                           user='root',
                                           password='1234')
        return conn

    def select_all_modules(self):
        conn = self.connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Module")
        rows = cur.fetchall()
        conn.close()
        return rows

    def select_module_by_id(self, id):
        conn = self.connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Module where ModuleID=" + str(id))
        row = cur.fetchone()
        conn.close()
        return row

    def select_module_by_name(self, name):
        conn = self.connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Module where Name=\'" + name + "\'")
        row = cur.fetchone()
        conn.close()
        return row

    def select_type_by_id(self, id):
        conn = self.connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT Name FROM VisualizationTypes where VisualizationTypeID=" + str(id))
        row = cur.fetchone()
        conn.close()
        return row

    def select_id_by_type(self, vtype):
        conn = self.connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT VisualizationTypeID FROM VisualizationTypes where Name='" + vtype + "'")
        row = cur.fetchone()
        conn.close()
        return row

    def select_all_type_info(self):
        conn = self.connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM VisualizationTypes")
        rows = cur.fetchall()
        conn.close()
        return rows

    def select_all_module_info(self):
        conn = self.connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Module")
        rows = cur.fetchall()
        conn.close()
        return rows

    def select_plot_details_by_module_id(self, id):
        conn = self.connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM PlotDetails where ModuleID=" + str(id))
        row = cur.fetchall()
        conn.close()
        return row

    def select_list_details_by_module_id(self, id):
        conn = self.connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM ListDetails where ModuleID=" + str(id))
        row = cur.fetchall()
        conn.close()
        return row

    def select_plot_signal_details_by_plot_id(self, id):
        conn = self.connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM PlotSignalDetails where PlotID=" + str(id))
        rows = cur.fetchall()
        conn.close()
        return rows

    def select_list_signal_details_by_list_id(self, id):
        conn = self.connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM ListSignalDetails where ListID=" + str(id))
        rows = cur.fetchall()
        conn.close()
        return rows

    def select_all_module_details_by_moduleid(self, id):
        conn = self.connect_to_db()
        cur = conn.cursor()
        query = "SELECT * FROM Module where TypeID=(SELECT TypeID FROM Module where ModuleID=" + str(id) + ")"
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        return rows

    def update_image_by_id(self, module_image, id):
        """
        Query all rows in the tasks table
        :param conn: the Connection object
        :return:
        """
        conn = self.connect_to_db()
        cur = conn.cursor()
        sql_query = "UPDATE Module SET Image=? WHERE ModuleID=?"
        module_image = self.convert_to_binary_data(module_image)

        cur.execute(sql_query, (module_image, id))
        internal_lastrowid = cur.lastrowid
        conn.commit()
        conn.close()
        return internal_lastrowid

    def convert_to_binary_data(self, image_file_name):
        with open(image_file_name, 'rb') as image_file_object:
            image_in_blob_format = image_file_object.read()
        return image_in_blob_format

    def create_module(self, name, description, author, date, image, typeid, revision, geometry_row, geometry_column):
        module_image = None
        file_extension = ""
        if os.path.exists(image):
            module_image = self.convert_to_binary_data(image)
            filename, file_extension = os.path.splitext(image)

        if geometry_row == "":
            geometry_row = "0"

        if geometry_column == "":
            geometry_column = "0"

        if DATABASE_SELECT == 'SQLITE':
            sql = '''
                    INSERT
                    INTO
                    Module(name, description, author, date, image,imagetype, revision, typeid, geometry)
                    VALUES(?, ?, ?, ?,?, ?,?,?,?)'''
            conn = self.connect_to_db()
            cur = conn.cursor()
            cur.execute(sql, (name, description, author, date, module_image, file_extension[1:], revision, typeid, "(" + geometry_row + "," + geometry_column + ")"))
            internal_lastrowid = cur.lastrowid
            conn.commit()
            conn.close()
            return internal_lastrowid
        elif DATABASE_SELECT == 'MYSQL':
            sql = '''
                    INSERT
                    INTO
                    Module(name, description, author, date, image,imagetype, revision, typeid, geometry)
                    VALUES(%s, %s, %s, %s,%s, %s,%s,%s,%s)'''
            conn = self.connect_to_db()
            cur = conn.cursor()
            cur.execute(sql, (name, description, author, date, module_image, file_extension[1:], revision, typeid,
                              "(" + geometry_row + "," + geometry_column + ")"))
            internal_lastrowid = cur.lastrowid
            conn.commit()
            conn.close()
            return internal_lastrowid


    def update_module(self, module_id, name, description, author, date, image, typeid, revision, geometry_row,
                      geometry_column):
        conn = self.connect_to_db()
        if geometry_row == "":
            geometry_row = "0"

        if geometry_column == "":
            geometry_column = "0"
        if os.path.exists(image):
            module_image = self.convert_to_binary_data(image)
            filename, file_extension = os.path.splitext(image)
            if DATABASE_SELECT == 'SQLITE':
                sql = '''UPDATE Module SET name = ? ,description = ?,author = ?,
                            date = ?, image = ? ,imagetype = ?,revision = ?,typeID = ?, Geometry = ?
                             WHERE moduleID = ? '''
                cur = conn.cursor()
                cur.execute(sql,
                            (name, description, author, date, module_image, file_extension[1:], revision, typeid,
                             "(" + geometry_row + "," + geometry_column + ")", module_id))
                internal_lastrowid = cur.lastrowid
            elif DATABASE_SELECT == 'MYSQL':
                sql = '''UPDATE Module SET name = %s ,description = %s,author = %s,
                           date = %s, image = %s ,imagetype = %s,revision = %s,typeID = %s, Geometry = %s
                            WHERE moduleID = %s '''
                cur = conn.cursor()
                cur.execute(sql,
                            (name, description, author, date, module_image, file_extension[1:], revision, typeid,
                             "(" + geometry_row + "," + geometry_column + ")", module_id))
                internal_lastrowid = cur.lastrowid
        else:
            if DATABASE_SELECT == 'SQLITE':
                sql = '''UPDATE Module SET name = ? ,description = ?,author = ?,
                            date = ?, revision = ?,typeID = ?, Geometry = ?
                             WHERE moduleID = ? '''
                cur = conn.cursor()
                cur.execute(sql,
                            (name, description, author, date, revision, typeid,
                             "(" + geometry_row + "," + geometry_column + ")", module_id))
                internal_lastrowid = cur.lastrowid
            elif DATABASE_SELECT == 'MYSQL':
                sql = '''UPDATE Module SET name = %s ,description = %s,author = %s,
                            date = %s, revision = %s,typeID = %s, Geometry = %s
                             WHERE moduleID = %s '''
                cur = conn.cursor()
                cur.execute(sql,
                            (name, description, author, date, revision, typeid,
                             "(" + geometry_row + "," + geometry_column + ")", module_id))
                internal_lastrowid = cur.lastrowid
        conn.commit()
        conn.close()
        return internal_lastrowid

    def delete_module(self, module_id):
        template_details = self.select_module_by_id(module_id)
        if template_details is not None:
            module_type = self.select_type_by_id(template_details[9])
            if module_type is not None:
                if module_type[0] == "List":
                    list_details = self.select_list_details_by_module_id(module_id)
                    if list_details is not None:
                        for list_detail in list_details:
                            self.delete_listdetails(list_detail[0])
                if module_type[0] == "Plot":
                    plot_details = self.select_plot_details_by_module_id(module_id)
                    if plot_details is not None:
                        for plot_detail in plot_details:
                            self.delete_axesdetails(plot_detail[0])

        conn = self.connect_to_db()
        cur = conn.cursor()
        sql = '''DELETE FROM Module WHERE  moduleID = 
																				''' + module_id
        cur.execute(sql)
        internal_lastrowid = cur.lastrowid
        conn.commit()
        conn.close()
        return internal_lastrowid

    def create_axesdetails(self, axesname, xlabel, ylabel, yticks, rownumber, columnnumber, module_id):
        conn = self.connect_to_db()
        if yticks.strip() == "":
            yticks = '{}'

        if DATABASE_SELECT == 'SQLITE':
            sql = '''
                    INSERT
                    INTO
                    PlotDetails(axesname, xlabel,ylabel,yticks,rownumber,columnnumber, moduleID)
                    VALUES(?, ?,?,?,?,?,?)'''

            cur = conn.cursor()
            cur.execute(sql, (axesname, xlabel, ylabel, yticks, rownumber, columnnumber, module_id))
            internal_lastrowid = cur.lastrowid
            conn.commit()
            conn.close()
            return internal_lastrowid
        elif DATABASE_SELECT == 'MYSQL':
            sql = '''
                    INSERT
                    INTO
                    PlotDetails(axesname, xlabel,ylabel,yticks,rownumber,columnnumber, moduleID)
                    VALUES(%s, %s,%s,%s,%s,%s,%s)'''
            cur = conn.cursor()
            cur.execute(sql, (axesname, xlabel, ylabel, yticks, rownumber, columnnumber, module_id))
            internal_lastrowid = cur.lastrowid
            conn.commit()
            conn.close()
            return internal_lastrowid


    def update_axesdetails(self, axesname, xlabel, ylabel, yticks, rownumber, columnnumber, plotdetail_id):
        conn = self.connect_to_db()
        if yticks.strip() == "":
            yticks = '{}'

        if DATABASE_SELECT == 'SQLITE':
            sql = '''
                    UPDATE PlotDetails
                    SET axesname = ?, xlabel =?,ylabel=?,yticks=?,rownumber=?,columnnumber=? WHERE  plotdetailID = ? 
                    '''
            cur = conn.cursor()
            cur.execute(sql, (axesname, xlabel, ylabel, yticks, rownumber, columnnumber, plotdetail_id))
            internal_lastrowid = cur.lastrowid
            conn.commit()
            conn.close()
            return internal_lastrowid
        elif DATABASE_SELECT == 'MYSQL':
            sql = '''
                    UPDATE PlotDetails
                    SET axesname = %s, xlabel =%s,ylabel=%s,yticks=%s,rownumber=%s,columnnumber=%s WHERE  plotdetailID = %s 
                    '''
            cur = conn.cursor()
            cur.execute(sql, (axesname, xlabel, ylabel, yticks, rownumber, columnnumber, plotdetail_id))
            internal_lastrowid = cur.lastrowid
            conn.commit()
            conn.close()
            return internal_lastrowid

    def delete_axesdetails(self, axes_detail_id):
        conn = self.connect_to_db()
        cur = conn.cursor()
        sql = '''DELETE FROM PlotSignalDetails WHERE  PlotID = 
																								''' + str(
            axes_detail_id)
        cur.execute(sql)
        conn.commit()

        cur = conn.cursor()
        sql = '''DELETE FROM PlotDetails WHERE  plotdetailID = 
																				''' + str(axes_detail_id)
        cur.execute(sql)
        internal_lastrowid = cur.lastrowid
        conn.commit()
        conn.close()
        return internal_lastrowid

    def create_listdetails(self, groupname, color, module_id):
        conn = self.connect_to_db()
        if DATABASE_SELECT == 'SQLITE':
            sql = '''
                    INSERT
                    INTO
                    ListDetails(groupname, backgroundColor,moduleID)
                    VALUES(?, ?,?)'''

            cur = conn.cursor()
            cur.execute(sql, (groupname, color, module_id))
            internal_lastrowid = cur.lastrowid
            conn.commit()
            conn.close()
            return internal_lastrowid
        elif DATABASE_SELECT == 'MYSQL':
            sql = '''
                    INSERT
                    INTO
                    ListDetails(groupname, backgroundColor,moduleID)
                    VALUES(%s, %s,%s)'''
            cur = conn.cursor()
            cur.execute(sql, (groupname, color, module_id))
            internal_lastrowid = cur.lastrowid
            conn.commit()
            conn.close()
            return internal_lastrowid

    def update_listdetails(self, groupname, backgroundColor, listdetail_id):
        conn = self.connect_to_db()
        if DATABASE_SELECT == 'SQLITE':
            sql = '''
                    UPDATE ListDetails
                    SET groupname = ?, backgroundColor =? WHERE  listdetailID = ? 
                    '''

            cur = conn.cursor()
            cur.execute(sql, (groupname, backgroundColor, listdetail_id))
            internal_lastrowid = cur.lastrowid
            conn.commit()
            conn.close()
            return internal_lastrowid
        elif DATABASE_SELECT == 'MYSQL':
            sql = '''
                      UPDATE ListDetails
                      SET groupname = %s, backgroundColor =%s WHERE  listdetailID = %s 
                      '''
            conn = self.connect_to_db()
            cur = conn.cursor()
            cur.execute(sql, (groupname, backgroundColor, listdetail_id))
            internal_lastrowid = cur.lastrowid
            conn.commit()
            conn.close()
            return internal_lastrowid

    def delete_listdetails(self, listdetail_id):
        conn = self.connect_to_db()
        cur = conn.cursor()
        sql = '''DELETE FROM ListSignalDetails WHERE  ListID = 
																				''' + str(listdetail_id)
        cur.execute(sql)
        conn.commit()

        sql = '''DELETE FROM ListDetails WHERE  listdetailID = 
																				''' + str(listdetail_id)
        cur.execute(sql)
        internal_lastrowid = cur.lastrowid
        conn.commit()
        conn.close()
        return internal_lastrowid

    def update_list_signal_details(self, id, signals, original_signals):
        conn = self.connect_to_db()
        cur = conn.cursor()
        for signal_key, signal_value in signals.items():
            if signal_key in original_signals.keys():
                if DATABASE_SELECT == 'SQLITE':
                    sql = '''
                            UPDATE ListSignalDetails
                            SET Label = ?, Offset =?,Factor = ?, DisplayScaled =?,Unit = ?, AliasName =?,DeviceName = ?, 
                            SignalName =?, IsCustomExpression =?,CustomExpression =?,CustomExpressionSignalList =?  WHERE  ListSignalDetailID = 
                            ''' + signal_key
                    cur.execute(sql, (
                        signal_value["Label"], signal_value["Offset"], signal_value["Factor"],
                        signal_value["DisplayScaled"],
                        signal_value["Unit"], signal_value["AliasName"], signal_value["DeviceName"],
                        signal_value["SignalName"], signal_value["IsCustomExpression"], signal_value["CustomExpression"],
                        str(signal_value["CustomExpressionSignalList"])))
                    conn.commit()
                elif DATABASE_SELECT == 'MYSQL':
                    sql = '''
                            UPDATE ListSignalDetails
                            SET Label = %s, Offset =%s,Factor = %s, DisplayScaled =%s,Unit = %s, AliasName =%s,DeviceName = %s, 
                            SignalName =%s, IsCustomExpression =%s,CustomExpression =%s,CustomExpressionSignalList =%s  WHERE  ListSignalDetailID = 
                            ''' + signal_key
                    cur.execute(sql, (
                        signal_value["Label"], signal_value["Offset"], signal_value["Factor"],
                        signal_value["DisplayScaled"],
                        signal_value["Unit"], signal_value["AliasName"], signal_value["DeviceName"],
                        signal_value["SignalName"], signal_value["IsCustomExpression"],
                        signal_value["CustomExpression"],
                        str(signal_value["CustomExpressionSignalList"])))
                    conn.commit()
            else:
                if not signal_key.isnumeric():
                    if DATABASE_SELECT == 'SQLITE':
                        sql = '''
                                INSERT
                                INTO
                                ListSignalDetails(Label, Offset,Factor,DisplayScaled,Unit, AliasName,DeviceName, SignalName, 
                                IsCustomExpression, CustomExpression,CustomExpressionSignalList,
                                ListID)
                                VALUES(?, ?,?,?, ?,?,?, ?,?,?,?,?)'''
                        conn = self.connect_to_db()
                        cur = conn.cursor()
                        cur.execute(sql, (signal_value["Label"], signal_value["Offset"], signal_value["Factor"],
                                          signal_value["DisplayScaled"], signal_value["Unit"], signal_value["AliasName"],
                                          signal_value["DeviceName"], signal_value["SignalName"],
                                          signal_value["IsCustomExpression"], signal_value["CustomExpression"],
                                          str(signal_value["CustomExpressionSignalList"]), id))
                        conn.commit()
                    elif DATABASE_SELECT == 'MYSQL':
                        sql = '''
                               INSERT
                               INTO
                               ListSignalDetails(Label, Offset,Factor,DisplayScaled,Unit, AliasName,DeviceName, SignalName, 
                               IsCustomExpression, CustomExpression,CustomExpressionSignalList,
                               ListID)
                               VALUES(%s, %s,%s,%s, %s,%s,%s, %s,%s,%s,%s,%s)'''
                        conn = self.connect_to_db()
                        cur = conn.cursor()
                        cur.execute(sql, (signal_value["Label"], signal_value["Offset"], signal_value["Factor"],
                                          signal_value["DisplayScaled"], signal_value["Unit"],
                                          signal_value["AliasName"],
                                          signal_value["DeviceName"], signal_value["SignalName"],
                                          signal_value["IsCustomExpression"], signal_value["CustomExpression"],
                                          str(signal_value["CustomExpressionSignalList"]), id))
                        conn.commit()
        for signal_key, signal_value in original_signals.items():
            if signal_key not in signals.keys():
                sql = '''DELETE FROM ListSignalDetails WHERE  ListSignalDetailID = 
																''' + signal_key
                cur.execute(sql)
                conn.commit()
        conn.close()

    def update_plot_signal_details(self, id, signals, original_signals):
        conn = self.connect_to_db()
        cur = conn.cursor()
        for signal_key, signal_value in signals.items():
            if signal_key in original_signals.keys():
                if DATABASE_SELECT == 'SQLITE':
                    sql = '''
                            UPDATE PlotSignalDetails
                            SET Label = ?, Offset =?,Factor = ?, DisplayScaled =?,Unit = ?, AliasName =?,DeviceName = ?, 
                            SignalName =?, IsCustomExpression =?,CustomExpression =?,CustomExpressionSignalList =? WHERE  PlotSignalDetailID = 
                            ''' + signal_key
                    cur.execute(sql, (
                        signal_value["Label"], signal_value["Offset"], signal_value["Factor"],
                        signal_value["DisplayScaled"],
                        signal_value["Unit"], signal_value["AliasName"], signal_value["DeviceName"],
                        signal_value["SignalName"], signal_value["IsCustomExpression"], signal_value["CustomExpression"],
                        str(signal_value["CustomExpressionSignalList"])))
                    conn.commit()
                elif DATABASE_SELECT == 'MYSQL':
                    sql = '''
                            UPDATE PlotSignalDetails
                            SET Label = %s, Offset =%s,Factor = %s, DisplayScaled =%s,Unit = %s, AliasName =%s,DeviceName = %s, 
                            SignalName =%s, IsCustomExpression =%s,CustomExpression =%s,CustomExpressionSignalList =%s WHERE  PlotSignalDetailID = 
                            ''' + signal_key
                    cur.execute(sql, (
                        signal_value["Label"], signal_value["Offset"], signal_value["Factor"],
                        signal_value["DisplayScaled"],
                        signal_value["Unit"], signal_value["AliasName"], signal_value["DeviceName"],
                        signal_value["SignalName"], signal_value["IsCustomExpression"],
                        signal_value["CustomExpression"],
                        str(signal_value["CustomExpressionSignalList"])))
                    conn.commit()
            else:
                if not signal_key.isnumeric():
                    if DATABASE_SELECT == 'SQLITE':
                        sql = '''
                                INSERT
                                INTO
                                PlotSignalDetails(Label, Offset,Factor,DisplayScaled,Unit, AliasName,DeviceName, SignalName, 
                                IsCustomExpression, CustomExpression, CustomExpressionSignalList,
                                PlotID)
                                VALUES(?, ?,?,?, ?,?,?, ?,?,?,?,?)'''
                        conn = self.connect_to_db()
                        cur = conn.cursor()
                        cur.execute(sql, (signal_value["Label"], signal_value["Offset"], signal_value["Factor"],
                                          signal_value["DisplayScaled"], signal_value["Unit"], signal_value["AliasName"],
                                          signal_value["DeviceName"], signal_value["SignalName"],
                                          signal_value["IsCustomExpression"], signal_value["CustomExpression"],
                                          str(signal_value["CustomExpressionSignalList"]), id))
                        conn.commit()
                    elif DATABASE_SELECT == 'MYSQL':
                        sql = '''
                               INSERT
                               INTO
                               PlotSignalDetails(Label, Offset,Factor,DisplayScaled,Unit, AliasName,DeviceName, SignalName, 
                               IsCustomExpression, CustomExpression, CustomExpressionSignalList,
                               PlotID)
                               VALUES(%s, %s,%s,%s, %s,%s,%s, %s,%s,%s,%s,%s)'''
                        conn = self.connect_to_db()
                        cur = conn.cursor()
                        cur.execute(sql, (signal_value["Label"], signal_value["Offset"], signal_value["Factor"],
                                          signal_value["DisplayScaled"], signal_value["Unit"],
                                          signal_value["AliasName"],
                                          signal_value["DeviceName"], signal_value["SignalName"],
                                          signal_value["IsCustomExpression"], signal_value["CustomExpression"],
                                          str(signal_value["CustomExpressionSignalList"]), id))
                        conn.commit()
        for signal_key, signal_value in original_signals.items():
            if signal_key not in signals.keys():
                sql = '''DELETE FROM PlotSignalDetails WHERE  PlotSignalDetailID = 
																''' + signal_key
                cur.execute(sql)
                conn.commit()
        conn.close()

    def fetch_signallist_by_plotid(self, plot_id):
        conn = self.connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM PlotSignalDetails WHERE PlotID = " + str(plot_id))
        rows = cur.fetchall()
        conn.close()
        return rows

    def add_signallist_by_plotid(self, plot_id, signals):
        conn = self.connect_to_db()
        cur = conn.cursor()
        for signal_value in signals:
            if DATABASE_SELECT == 'SQLITE':
                sql = '''
                                                                                        INSERT
                                                                                        INTO
                                                                                        PlotSignalDetails(Label, Offset,Factor,DisplayScaled,Unit, AliasName,
                                                                                        DeviceName, SignalName, IsCustomExpression, CustomExpression, CustomExpressionSignalList,
                                                                                        PlotID)
                                                                                        VALUES(?, ?,?,?, ?,?,?, ?,?,?,?,?)'''
                cur = conn.cursor()
                cur.execute(sql, (signal_value[1], signal_value[2], signal_value[3],
                                  signal_value[4], signal_value[5], signal_value[6],
                                  signal_value[7], signal_value[8], signal_value[9], signal_value[10], signal_value[11],
                                  plot_id))
                conn.commit()
            elif DATABASE_SELECT == 'MYSQL':
                sql = '''
                                                                                        INSERT
                                                                                        INTO
                                                                                        PlotSignalDetails(Label, Offset,Factor,DisplayScaled,Unit, AliasName,
                                                                                        DeviceName, SignalName, IsCustomExpression, CustomExpression, CustomExpressionSignalList,
                                                                                        PlotID)
                                                                                        VALUES(%s, %s,%s,%s, %s,%s,%s, %s,%s,%s,%s,%s)'''
                cur = conn.cursor()
                cur.execute(sql, (signal_value[1], signal_value[2], signal_value[3],
                                  signal_value[4], signal_value[5], signal_value[6],
                                  signal_value[7], signal_value[8], signal_value[9], signal_value[10], signal_value[11],
                                  plot_id))
                conn.commit()
        conn.close()
        return

    def fetch_signallist_by_listid(self, list_id):
        conn = self.connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM ListSignalDetails WHERE ListID = " + str(list_id))
        rows = cur.fetchall()
        conn.close()
        return rows

    def add_signallist_by_listid(self, list_id, signals):
        conn = self.connect_to_db()
        cur = conn.cursor()
        for signal_value in signals:
            if DATABASE_SELECT == 'SQLITE':
                sql = '''
                                                                                        INSERT
                                                                                        INTO
                                                                                        ListSignalDetails(Label, Offset,Factor,DisplayScaled,Unit, AliasName,
                                                                                        DeviceName, SignalName, IsCustomExpression, CustomExpression, CustomExpressionSignalList,
                                                                                        ListID)
                                                                                        VALUES(?, ?,?,?, ?,?,?, ?,?,?,?,?)'''
                cur.execute(sql, (signal_value[1], signal_value[2], signal_value[3],
                                  signal_value[4], signal_value[5], signal_value[6],
                                  signal_value[7], signal_value[8], signal_value[9], signal_value[10], signal_value[11],
                                  list_id))
                conn.commit()
            elif DATABASE_SELECT == 'MYSQL':
                sql = '''
                                                                                        INSERT
                                                                                        INTO
                                                                                        ListSignalDetails(Label, Offset,Factor,DisplayScaled,Unit, AliasName,
                                                                                        DeviceName, SignalName, IsCustomExpression, CustomExpression, CustomExpressionSignalList,
                                                                                        ListID)
                                                                                        VALUES(%s, %s,%s,%s, %s,%s,%s, %s,%s,%s,%s,%s)'''
                cur.execute(sql, (signal_value[1], signal_value[2], signal_value[3],
                                  signal_value[4], signal_value[5], signal_value[6],
                                  signal_value[7], signal_value[8], signal_value[9], signal_value[10], signal_value[11],
                                  list_id))
                conn.commit()
        conn.close()
        return

