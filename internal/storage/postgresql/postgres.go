package postgresql

import (
	"CourseWork/lib/types"
	"database/sql"
	"fmt"
	_ "github.com/jackc/pgx/stdlib"
	"github.com/jmoiron/sqlx"
	"log"
	"sync"
	"time"
)

type Postgres struct {
	db *sql.DB
}

type PostgresSqlx struct {
	db *sqlx.DB
}

var (
	pgInstance *PostgresSqlx
	pgOnce     sync.Once
)

func (pg *PostgresSqlx) CheckDateTimeDB(limitUp, limitLow time.Time, date time.Time) (error, []time.Time) {
	const funcName = "/internal/storage/postgresql/CheckDateTime"

	dateValue := time.Date(date.Year(), date.Month(), date.Day(), date.Hour(), date.Minute(), date.Second(), 0, time.Local) // Преобразуйте в time.Time
	dateVal := dateValue.Format(time.DateOnly)
	fmt.Println(dateValue.Format(time.DateOnly))
	limitup := limitUp.Format(time.TimeOnly)
	limitlow := limitLow.Format(time.TimeOnly)
	fmt.Println(limitup, limitlow, limitLow)
	//query := fmt.Sprintf(`SELECT EXISTS(SELECT 1 FROM appointments WHERE event_time BETWEEN TIMESTAMP '%s' - INTERVAL '1 hour' AND TIMESTAMP '%s' + INTERVAL '1 hour');`, dateValue.Format("2006-01-02 15:04:05"), dateValue.Format("2006-01-02 15:04:05"))
	//query := `SELECT event_time FROM appointments WHERE date(event_time) = $1`
	query := fmt.Sprintf(`SELECT event_time FROM appointments WHERE event_time BETWEEN '%sT%s' AND '%sT%s'`, dateVal, limitup, dateVal, limitlow)
	//query := `SELECT EXISTS(SELECT 1 FROM appointments WHERE event_time BETWEEN TIMESTAMP $1 - INTERVAL '1 hour' AND TIMESTAMP $1 + INTERVAL '1 hour');`
	fmt.Println(query)
	rows, err := pg.db.Query(query)
	if err != nil {
		fmt.Println(err)
		return err, nil
	}
	defer rows.Close()
	var times []time.Time
	for rows.Next() {
		var scanTime time.Time
		if err = rows.Scan(&scanTime); err != nil {
			log.Println(err)
		}
		times = append(times, scanTime)
	}
	fmt.Println(times)
	//_ = pg.db.QueryRow(query).Scan(&exists)
	return nil, times
}

func (pg *PostgresSqlx) NewAppointment(appoint types.Appointment) error {
	const funcName = "/internal/storage/postgresql/NewAppointment"
	query := `INSERT INTO appointments (firstname, midname, lastname, service, event_time, online) VALUES ($1, $2, $3, $4, $5, $6)`
	dateValue := appoint.Datetime.Format("2006-01-02 15:04:05")

	_, err := pg.db.Exec(query, appoint.FirstName, appoint.MidName, appoint.LastName, appoint.Service, dateValue, appoint.Online)
	if err != nil {
		log.Printf("Error appending new appointment into database: %v, %s", err, funcName)
	}
	return err
}

func (pg *PostgresSqlx) GetAppointments() ([]types.Appointment, error) {
	const funcName = "/internal/storage/postgresql/NewAppointment"
	query := `SELECT * FROM appointments`
	rows, err := pg.db.Query(query)
	if err != nil {
		fmt.Println(err)
		return nil, err
	}
	defer rows.Close()
	var appointments []types.Appointment
	for rows.Next() {
		var appointment types.Appointment

		if err = rows.Scan(&appointment.Id, &appointment.FirstName, &appointment.MidName, &appointment.LastName, &appointment.Service, &appointment.Datetime, &appointment.Online); err != nil {
			log.Println(err)
		}
		appointments = append(appointments, appointment)
	}
	fmt.Println(appointments)
	return appointments, err
}

func NewPG(connString string) (*PostgresSqlx, error) {
	var err error
	pgOnce.Do(func() {
		db, err := sqlx.Open("pgx", connString)
		if err != nil {
			log.Printf("Error opening database connection: %v", err)
			return // Immediately return on error
		}

		// Check the connection immediately
		err = db.Ping()
		if err != nil {
			_ = db.Close() // Close the connection if Ping fails
			log.Printf("Error pinging database: %v", err)
			return // Immediately return on error
		}

		pgInstance = &PostgresSqlx{db: db}
		if pgInstance == nil {
			err = fmt.Errorf("unable to create connection")
			return
		}

		log.Println("Database connection successful:", pgInstance)
	})
	return pgInstance, err
}

func makeAnAppointment() {

}
