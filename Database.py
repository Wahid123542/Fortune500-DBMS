import csv
import os.path

class DB:

    # Default constructor
    def __init__(self):
        self.filestream = None
        self.numSortedRecords = -1  # Number of records in sorted order
        self.numUnsortedRecords = 0  # Number of records added to overflow area
        self.numRecords = -1  # Total records
        self.recordSize = -1
        self.name_of_db = ""  # Keep the database name for the config file

    
    # Write a fixed-length record to the file
    # Fields: NAME(55) + RANK(4) + CITY(20) + STATE(2) + ZIP(10) + EMPLOYEES(8) + newline(1) = 100 bytes
    def writeRecord(self, filestream, name, rank, city, state, zip_code, employees):
        try:
            filestream.write("{:55.55}".format(name))
            filestream.write("{:4.4}".format(rank))
            filestream.write("{:20.20}".format(city))
            filestream.write("{:2.2}".format(state))
            filestream.write("{:10.10}".format(zip_code))
            filestream.write("{:8.8}".format(employees))
            filestream.write("\n")
            return True
        except IOError:
            return False
        
    # Create database from CSV file
    def createDB(self, filename):
        # Generate file names
        csv_filename = filename + ".csv"
        data_filename = filename + ".data"
        config_filename = filename + ".config"

        # Set the record size for the fixed length file (100 bytes)
        self.recordSize = 100
        count = 0  # Count how many records are written
        self.name_of_db = filename  # Save the database name for later

        # Read the CSV file line by line and write into data file
        with open(csv_filename, "r") as csv_file, open(data_filename, "w", newline="\n") as outfile:

            for line in csv_file: 
                csv_reader = csv.reader([line])
                row = next(csv_reader)

                # Write the Fortune500 record with 6 fields
                self.writeRecord(outfile, row[0], row[1], row[2], row[3], row[4], row[5])
                count += 1

        self.numSortedRecords = count  # All records from CSV are sorted
        self.numUnsortedRecords = 0  # No unsorted records initially
        self.numRecords = count  # Total records

        # Write config file with sorted and unsorted counts
        with open(config_filename, "w", newline="\n") as out:
            out.write(str(self.numSortedRecords) + "\n")
            out.write(str(self.numUnsortedRecords) + "\n")
            out.write(str(self.recordSize) + "\n")
            out.write(self.name_of_db + "\n")

        return True

   	
    # Open the database by reading config and opening data file
    def open(self, filename):
        data_filename = filename + ".data"
        config_filename = filename + ".config"
        
        # Check if the data file exists
        if not os.path.isfile(data_filename):
            print(str(data_filename) + " not found")
            return False
        
        # Check if the config file exists
        if not os.path.isfile(config_filename): 
            print(str(config_filename) + " not found")
            return False
        
        # Read numSortedRecords, numUnsortedRecords, and recordSize from the config file
        with open(config_filename, "r") as out:
            self.numSortedRecords = int(out.readline().strip())
            self.numUnsortedRecords = int(out.readline().strip())
            self.recordSize = int(out.readline().strip())
            self.name_of_db = out.readline().strip()

        self.numRecords = self.numSortedRecords + self.numUnsortedRecords
        
        # Open the data file so records can be found, read, and written 
        self.filestream = open(data_filename, 'r+', newline="\n")
        return True
            

    # Read a record at a specific position
    def readRecord(self, recordNum, name, rank, city, state, zip_code, employees):
        status = False  # Assume failure until successful read

        # Check if recordNum is valid
        if 0 <= recordNum < self.numRecords:
            # Jump to where the record starts
            self.filestream.seek(recordNum * self.recordSize)

            # Read the record line and remove newline chars
            line = self.filestream.readline().rstrip('\n').rstrip('\r')

            # Split the record into fields using the 100-byte layout
            name[0] = line[0:55].strip()
            rank[0] = line[55:59].strip()
            city[0] = line[59:79].strip()
            state[0] = line[79:81].strip()
            zip_code[0] = line[81:91].strip()
            employees[0] = line[91:99].strip()

            status = True
            
        return status


    # Binary search for a record by name in the SORTED portion of the file
    def binarySearch(self, search_name, name, rank, city, state, zip_code, employees):
        """
        Binary search on sorted records (0 to numSortedRecords-1)
        Returns: recordNum if found, -1 if not found
        """
        if self.filestream is None:
            return -1

        low = 0
        high = self.numSortedRecords - 1

        while low <= high:
            mid = (low + high) // 2
            
            # Read the record at mid position
            temp_name = ['']
            temp_rank = ['']
            temp_city = ['']
            temp_state = ['']
            temp_zip = ['']
            temp_employees = ['']
            
            self.readRecord(mid, temp_name, temp_rank, temp_city, temp_state, temp_zip, temp_employees)
            
            # Skip deleted records and compare names
            mid_name = temp_name[0].strip()
            search_key = search_name.strip()
            
            # Compare names (case-insensitive)
            if mid_name.lower() == search_key.lower():
                # Found it! Fill in the output parameters
                name[0] = temp_name[0]
                rank[0] = temp_rank[0]
                city[0] = temp_city[0]
                state[0] = temp_state[0]
                zip_code[0] = temp_zip[0]
                employees[0] = temp_employees[0]
                return mid
            elif mid_name.lower() < search_key.lower():
                low = mid + 1
            else:
                high = mid - 1

        # Not found
        return -1


    # Linear search for a record by name in the UNSORTED portion of the file
    def linearSearch(self, search_name, name, rank, city, state, zip_code, employees):
        """
        Linear search on unsorted records (numSortedRecords to numRecords-1)
        Returns: recordNum if found, -1 if not found
        """
        if self.filestream is None:
            return -1

        # Search only the unsorted portion
        for recordNum in range(self.numSortedRecords, self.numRecords):
            temp_name = ['']
            temp_rank = ['']
            temp_city = ['']
            temp_state = ['']
            temp_zip = ['']
            temp_employees = ['']
            
            self.readRecord(recordNum, temp_name, temp_rank, temp_city, temp_state, temp_zip, temp_employees)
            
            # Compare names (case-insensitive)
            if temp_name[0].lower() == search_name.lower():
                # Found it! Fill in the output parameters
                name[0] = temp_name[0]
                rank[0] = temp_rank[0]
                city[0] = temp_city[0]
                state[0] = temp_state[0]
                zip_code[0] = temp_zip[0]
                employees[0] = temp_employees[0]
                return recordNum

        # Not found
        return -1


    # Find a record by name (searches both sorted and unsorted portions)
    def findRecord(self, search_name, name, rank, city, state, zip_code, employees):
        """
        First tries binary search on sorted records, then linear search on unsorted records
        Returns: recordNum if found, -1 if not found
        """
        if self.filestream is None:
            return -1

        # First try binary search on sorted records
        recordNum = self.binarySearch(search_name, name, rank, city, state, zip_code, employees)
        
        if recordNum != -1:
            return recordNum

        # If not found in sorted records, try linear search on unsorted records
        recordNum = self.linearSearch(search_name, name, rank, city, state, zip_code, employees)
        
        if recordNum == -1:
            # Set default values if not found
            name[0] = ""
            rank[0] = ""
            city[0] = ""
            state[0] = ""
            zip_code[0] = ""
            employees[0] = ""

        return recordNum


    # Update an existing record
    def updateRecord(self, search_name, new_rank, new_city, new_state, new_zip, new_employees):
        """
        Find and update a record. Name cannot be changed (it's the primary key)
        Returns: True if updated, False if record not found or DB not open
        """
        if self.filestream is None:
            return False

        # Find the record
        name = ['']
        rank = ['']
        city = ['']
        state = ['']
        zip_code = ['']
        employees = ['']
        
        recordNum = self.findRecord(search_name, name, rank, city, state, zip_code, employees)
        
        if recordNum == -1:
            return False  # Record not found

        # Seek to the record position and overwrite it
        self.filestream.seek(recordNum * self.recordSize)
        self.writeRecord(self.filestream, name[0], new_rank, new_city, new_state, new_zip, new_employees)
        self.filestream.flush()  # Make sure changes are written to disk
        
        return True


    # Delete a record (logical delete - blank out fields except name)
    def deleteRecord(self, search_name):
        """
        Logically delete a record by blanking all fields except name
        (Name must stay to preserve binary search order)
        Returns: True if deleted, False if record not found or DB not open
        """
        if self.filestream is None:
            return False

        # Find the record
        name = ['']
        rank = ['']
        city = ['']
        state = ['']
        zip_code = ['']
        employees = ['']
        
        recordNum = self.findRecord(search_name, name, rank, city, state, zip_code, employees)
        
        if recordNum == -1:
            return False  # Record not found

        # Seek to the record position and overwrite with blanks (except name)
        self.filestream.seek(recordNum * self.recordSize)
        self.writeRecord(self.filestream, name[0], "", "", "", "", "")
        self.filestream.flush()
        
        return True


    # Add a new record to the end of the file (unsorted area)
    def addRecord(self, name, rank, city, state, zip_code, employees):
        """
        Add a new record to the end of the file (unsorted area)
        Returns: True if successful, False if DB not open
        """
        if self.filestream is None:
            return False

        # Seek to end of file
        self.filestream.seek(0, 2)  # 2 = end of file
        
        # Write the new record
        self.writeRecord(self.filestream, name, rank, city, state, zip_code, employees)
        self.filestream.flush()
        
        # Update counts
        self.numUnsortedRecords += 1
        self.numRecords += 1
        
        return True


    # Check if database is open
    def isOpen(self):
        return self.filestream is not None


    # Close the database
    def close(self):
        # Save all current info back to the config file
        if self.name_of_db is not None:
            config_filename = self.name_of_db + ".config"

            with open(config_filename, "w", newline="\n") as out:
                out.write(str(self.numSortedRecords) + "\n")
                out.write(str(self.numUnsortedRecords) + "\n")
                out.write(str(self.recordSize) + "\n")
                out.write(self.name_of_db + "\n")

        # Close the data file if it's open
        if self.filestream is not None:
            self.filestream.close()

        # Reset everything so the database is closed
        self.filestream = None
        self.numSortedRecords = -1
        self.numUnsortedRecords = 0
        self.numRecords = -1
        self.recordSize = -1
        self.name_of_db = None


    # Print a report of the first 10 records
    def printReport(self):
        """
        Display the first 10 records in a nicely formatted table
        """
        if self.filestream is None:
            print("Error: No database is open")
            return

        print("\n" + "="*120)
        print("DATABASE REPORT - First 10 Records")
        print("="*120)
        print(f"{'NAME':<55} {'RANK':<6} {'CITY':<20} {'ST':<4} {'ZIP':<12} {'EMPLOYEES':<10}")
        print("-"*120)

        # Display up to 10 records
        max_display = min(10, self.numRecords)
        
        for i in range(max_display):
            name = ['']
            rank = ['']
            city = ['']
            state = ['']
            zip_code = ['']
            employees = ['']
            
            if self.readRecord(i, name, rank, city, state, zip_code, employees):
                print(f"{name[0]:<55} {rank[0]:<6} {city[0]:<20} {state[0]:<4} {zip_code[0]:<12} {employees[0]:<10}")

        print("="*120)
        print(f"Total records in database: {self.numRecords} (Sorted: {self.numSortedRecords}, Unsorted: {self.numUnsortedRecords})")
        print()


# Main program with menu
def main():
    db = DB()
    
    while True:
        print("\n" + "="*50)
        print("DATABASE MANAGEMENT SYSTEM")
        print("="*50)
        print("1) Create new database")
        print("2) Open database")
        print("3) Close database")
        print("4) Display record")
        print("5) Update record")
        print("6) Print report to the screen")
        print("7) Add record")
        print("8) Delete record")
        print("9) Quit")
        print("="*50)
        
        choice = input("Enter your choice (1-9): ").strip()
        
        if choice == '1':
            # Create new database
            filename = input("Enter the name of the CSV file (without .csv extension): ").strip()
            if db.createDB(filename):
                print(f"Database '{filename}' created successfully!")
            else:
                print("Error creating database")
                
        elif choice == '2':
            # Open database
            if db.isOpen():
                print("Error: A database is already open. Please close it first.")
            else:
                filename = input("Enter the database name to open: ").strip()
                if db.open(filename):
                    print(f"Database '{filename}' opened successfully!")
                    print(f"Records: {db.numRecords} (Sorted: {db.numSortedRecords}, Unsorted: {db.numUnsortedRecords})")
                else:
                    print("Error opening database")
                    
        elif choice == '3':
            # Close database
            if not db.isOpen():
                print("Error: No database is open")
            else:
                db.close()
                print("Database closed successfully")
                
        elif choice == '4':
            # Display record
            if not db.isOpen():
                print("Error: No database is open")
            else:
                search_name = input("Enter company name to display: ").strip()
                
                name = ['']
                rank = ['']
                city = ['']
                state = ['']
                zip_code = ['']
                employees = ['']
                
                recordNum = db.findRecord(search_name, name, rank, city, state, zip_code, employees)
                
                if recordNum != -1:
                    print("\n" + "="*80)
                    print(f"Record found at position {recordNum}:")
                    print("="*80)
                    print(f"NAME:      {name[0]}")
                    print(f"RANK:      {rank[0]}")
                    print(f"CITY:      {city[0]}")
                    print(f"STATE:     {state[0]}")
                    print(f"ZIP:       {zip_code[0]}")
                    print(f"EMPLOYEES: {employees[0]}")
                    print("="*80)
                else:
                    print(f"Record with name '{search_name}' not found")
                    
        elif choice == '5':
            # Update record
            if not db.isOpen():
                print("Error: No database is open")
            else:
                search_name = input("Enter company name to update: ").strip()
                
                # First find and display the record
                name = ['']
                rank = ['']
                city = ['']
                state = ['']
                zip_code = ['']
                employees = ['']
                
                recordNum = db.findRecord(search_name, name, rank, city, state, zip_code, employees)
                
                if recordNum != -1:
                    print("\nCurrent record:")
                    print(f"NAME:      {name[0]} (cannot be changed)")
                    print(f"RANK:      {rank[0]}")
                    print(f"CITY:      {city[0]}")
                    print(f"STATE:     {state[0]}")
                    print(f"ZIP:       {zip_code[0]}")
                    print(f"EMPLOYEES: {employees[0]}")
                    
                    print("\nEnter new values (press Enter to keep current value):")
                    new_rank = input(f"New RANK [{rank[0]}]: ").strip() or rank[0]
                    new_city = input(f"New CITY [{city[0]}]: ").strip() or city[0]
                    new_state = input(f"New STATE [{state[0]}]: ").strip() or state[0]
                    new_zip = input(f"New ZIP [{zip_code[0]}]: ").strip() or zip_code[0]
                    new_employees = input(f"New EMPLOYEES [{employees[0]}]: ").strip() or employees[0]
                    
                    if db.updateRecord(name[0], new_rank, new_city, new_state, new_zip, new_employees):
                        print("Record updated successfully!")
                    else:
                        print("Error updating record")
                else:
                    print(f"Record with name '{search_name}' not found")
                    
        elif choice == '6':
            # Print report
            if not db.isOpen():
                print("Error: No database is open")
            else:
                db.printReport()
                
        elif choice == '7':
            # Add record
            if not db.isOpen():
                print("Error: No database is open")
            else:
                print("\nEnter new record information:")
                name = input("NAME: ").strip()
                rank = input("RANK: ").strip()
                city = input("CITY: ").strip()
                state = input("STATE: ").strip()
                zip_code = input("ZIP: ").strip()
                employees = input("EMPLOYEES: ").strip()
                
                if db.addRecord(name, rank, city, state, zip_code, employees):
                    print("Record added successfully!")
                    print(f"New total: {db.numRecords} records (Sorted: {db.numSortedRecords}, Unsorted: {db.numUnsortedRecords})")
                else:
                    print("Error adding record")
                    
        elif choice == '8':
            # Delete record
            if not db.isOpen():
                print("Error: No database is open")
            else:
                search_name = input("Enter company name to delete: ").strip()
                
                if db.deleteRecord(search_name):
                    print(f"Record '{search_name}' deleted successfully!")
                else:
                    print(f"Record with name '{search_name}' not found")
                    
        elif choice == '9':
            # Quit
            if db.isOpen():
                db.close()
                print("Database closed")
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter 1-9")


if __name__ == "__main__":
    main()