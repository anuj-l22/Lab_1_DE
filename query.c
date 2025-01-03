#include <mysql.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
 // gcc -o query query.c -I"C:\Program Files\MySQL\MySQL Server 9.0\include" "C:\Program Files\MySQL\MySQL Server 9.0\lib\libmysql.dll"
// Function to handle errors
void finish_with_error(MYSQL *con) {
    fprintf(stderr, "%s\n", mysql_error(con));
    mysql_close(con);
    exit(1);
}

// Function to calculate the time difference
double calculate_time(struct timespec start, struct timespec end) {
    return (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
}

void execute_query(MYSQL *con, const char* query, const char* task_description, const char* query_type) {
    // Print task description and query type
    printf("%s\n", task_description);
    printf("Executing %s query...\n", query_type);

    // Measure start time
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    // Execute query
    if (mysql_query(con, query)) {
        finish_with_error(con);
    }

    MYSQL_RES *result = mysql_store_result(con);

    if (result == NULL) {
        finish_with_error(con);
    }

    // Print the results
    int num_fields = mysql_num_fields(result);
    MYSQL_ROW row;
    while ((row = mysql_fetch_row(result))) {
        for(int i = 0; i < num_fields; i++) {
            printf("%s ", row[i] ? row[i] : "NULL");
        }
        printf("\n");
    }

    // Measure end time and print execution time
    clock_gettime(CLOCK_MONOTONIC, &end);
    double time_taken = calculate_time(start, end);
    printf("%s Execution Time: %.6f seconds\n", query_type, time_taken);

    mysql_free_result(result);
}

int main() {
    MYSQL *con = mysql_init(NULL);

    if (con == NULL) {
        fprintf(stderr, "mysql_init() failed\n");
        return 1;
    }

    // Replace with your environment variables or static credentials
    const char* host = getenv("MYSQL_HOST");
    const char* user = getenv("MYSQL_USER");
    const char* password = getenv("MYSQL_PASSWORD");
    const char* database = getenv("MYSQL_DATABASE");

    if (mysql_real_connect(con, host, user, password, database, 0, NULL, 0) == NULL) {
        finish_with_error(con);
    }

    // Queries for Task 1
    const char* task1_unoptimized = "SELECT DISTINCT CarID, CarType "
                                    "FROM CombinedBookingsView "
                                    "WHERE CarID IN ("
                                    "    SELECT CarID "
                                    "    FROM ("
                                    "        SELECT CarID, MONTH(BookingDate) AS BookingMonth "
                                    "        FROM CombinedBookingsView "
                                    "        WHERE YEAR(BookingDate) = 2023"
                                    "    ) AS MonthlyBookings "
                                    "    GROUP BY CarID "
                                    "    HAVING COUNT(DISTINCT BookingMonth) = 12"
                                    ");";


    const char* task1_optimized = "SELECT CarID, CarType "
                                  "FROM ("
                                  "    SELECT CarID, CarType, COUNT(DISTINCT MONTH(BookingDate)) AS MonthCount "
                                  "    FROM CombinedBookingsView "
                                  "    WHERE YEAR(BookingDate) = 2023 "
                                  "    AND CarID IS NOT NULL "
                                  "    GROUP BY CarID, CarType "
                                  ") AS CarMonthCounts "
                                  "WHERE MonthCount = 12;";

    const char* task_description_1 = "Task 1: Extract a list of all <car_number, type> who had bookings in all months in 2023";
    execute_query(con, task1_unoptimized, task_description_1, "Unoptimized");
    execute_query(con, task1_optimized, task_description_1, "Optimized");

    // Queries for Task 2
    const char* task2_unoptimized = "SELECT CarID, CarType "
                                    "FROM CombinedBookingsView "
                                    "WHERE CarID IN ("
                                    "    SELECT CarID "
                                    "    FROM CombinedBookingsView "
                                    "    WHERE YEAR(BookingDate) = 2023 "
                                    "    GROUP BY CarID, CarType "
                                    "    HAVING COUNT(DISTINCT MONTH(BookingDate)) = 12"
                                    ") "
                                    "AND FlightID IS NOT NULL;";

    const char* task2_optimized = "SELECT DISTINCT cbv.CarID, cbv.CarType "
                                  "FROM CombinedBookingsView AS cbv "
                                  "JOIN ("
                                  "    SELECT CarID, CarType "
                                  "    FROM CombinedBookingsView "
                                  "    WHERE YEAR(BookingDate) = 2023 "
                                  "    AND CarID IS NOT NULL "
                                  "    GROUP BY CarID, CarType "
                                  "    HAVING COUNT(DISTINCT MONTH(BookingDate)) = 12"
                                  ") AS AllMonthsCars ON cbv.CarID = AllMonthsCars.CarID AND cbv.CarType = AllMonthsCars.CarType "
                                  "WHERE cbv.FlightID IS NOT NULL;";

    const char* task_description_2 = "Task 2: From the above list, print the names of all car_numbers who were associated with a flight booking";
    execute_query(con, task2_unoptimized, task_description_2, "Unoptimized");
    execute_query(con, task2_optimized, task_description_2, "Optimized");

    // Queries for Task 3
    const char* task3_unoptimized = "SELECT h.HotelID, h.HotelName, h.City, h.PricePerNight "
                                    "FROM Hotel AS h "
                                    "LEFT JOIN Artwork AS a ON h.HotelID = a.hotel_id "
                                    "WHERE a.hotel_id IS NULL;";

    const char* task3_optimized = "SELECT h.HotelID, h.HotelName, h.City, h.PricePerNight "
                                  "FROM ("
                                  "    SELECT HotelID, HotelName, City, PricePerNight "
                                  "    FROM Hotel "
                                  ") AS h "
                                  "LEFT JOIN ("
                                  "    SELECT hotel_id FROM Artwork "
                                  ") AS a ON h.HotelID = a.hotel_id "
                                  "WHERE a.hotel_id IS NULL;";

    const char* task_description_3 = "Task 3: Extract a list of all <hotel> information for whom the database does not have any artwork listing";
    execute_query(con, task3_unoptimized, task_description_3, "Unoptimized");
    execute_query(con, task3_optimized, task_description_3, "Optimized");

    // Queries for Task 4
    const char* task4_unoptimized = "SELECT DISTINCT u.UserID "
                                    "FROM User AS u "
                                    "JOIN CombinedBookingsView AS cbv1 ON u.UserID = cbv1.UserID "
                                    "JOIN CombinedBookingsView AS cbv2 ON u.UserID = cbv2.UserID "
                                    "JOIN CombinedBookingsView AS cbv3 ON u.UserID = cbv3.UserID "
                                    "JOIN Hotel AS h ON cbv3.HotelID = h.HotelID "
                                    "WHERE "
                                    "    YEAR(cbv1.BookingDate) = 2022 "
                                    "    AND cbv2.CarType = 'Innova' "
                                    "    AND h.RoomType = 'Single Room';";

    const char* task4_optimized = "SELECT DISTINCT cbv.UserID "
                                  "FROM CombinedBookingsView AS cbv "
                                  "JOIN Hotel AS h ON cbv.HotelID = h.HotelID "
                                  "WHERE "
                                  "    YEAR(cbv.BookingDate) = 2022 "
                                  "    AND cbv.CarType = 'Innova' "
                                  "    AND h.RoomType = 'Single Room';";

    const char* task_description_4 = "Task 4: Print a list of all guests who have made a booking of ‘single_room’ + ‘innova’ in 2022";
    execute_query(con, task4_unoptimized, task_description_4, "Unoptimized");
    execute_query(con, task4_optimized, task_description_4, "Optimized");

    // Queries for Task 5
    const char* task5_unoptimized = "SELECT DISTINCT u.UserID, u.Name AS GuestName, u.Email, u.ContactNumber "
                                    "FROM User AS u "
                                    "JOIN CombinedBookingsView AS cbv1 ON u.UserID = cbv1.UserID "
                                    "JOIN CombinedBookingsView AS cbv2 ON u.UserID = cbv2.UserID "
                                    "JOIN CombinedBookingsView AS cbv3 ON u.UserID = cbv3.UserID "
                                    "JOIN Hotel AS h ON cbv3.HotelID = h.HotelID "
                                    "WHERE "
                                    "    YEAR(cbv1.BookingDate) = 2022 "
                                    "    AND cbv2.CarType = 'Innova' "
                                    "    AND h.RoomType = 'Single Room';";

    const char* task5_optimized = "SELECT DISTINCT u.UserID, u.Name AS GuestName, u.Email, u.ContactNumber "
                                  "FROM CombinedBookingsView AS cbv "
                                  "JOIN Hotel AS h ON cbv.HotelID = h.HotelID "
                                  "JOIN User AS u ON cbv.UserID = u.UserID "
                                  "WHERE "
                                  "    YEAR(cbv.BookingDate) = 2022 "
                                  "    AND cbv.CarType = 'Innova' "
                                  "    AND h.RoomType = 'Single Room';";

    const char* task_description_5 = "Task 5: From the above list, derive a list of the guest_name and their profile information";
    execute_query(con, task5_unoptimized, task_description_5, "Unoptimized");
    execute_query(con, task5_optimized, task_description_5, "Optimized");

    // Queries for Task 6
    const char* task6_unoptimized = "SELECT u.UserID, u.Name AS GuestName, u.Email, u.ContactNumber "
                                    "FROM User AS u "
                                    "LEFT JOIN Booking AS b ON u.UserID = b.UserID "
                                    "WHERE b.UserID IS NULL;";

    const char* task6_optimized = "SELECT u.UserID, u.Name AS GuestName, u.Email, u.ContactNumber "
                                  "FROM User AS u "
                                  "WHERE NOT EXISTS ("
                                  "    SELECT 1 "
                                  "    FROM Booking AS b "
                                  "    WHERE b.UserID = u.UserID"
                                  ");";

    const char* task_description_6 = "Task 6: Derive a list of all <guest_profiles> who have not made any bookings";
    execute_query(con, task6_unoptimized, task_description_6, "Unoptimized");
    execute_query(con, task6_optimized, task_description_6, "Optimized");

    // Close connection
    mysql_close(con);

    return 0;
}
