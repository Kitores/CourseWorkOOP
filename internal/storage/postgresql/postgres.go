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

func (pg *PostgresSqlx) CheckDateTimeDB(date types.Date) (error, bool) {
	var exists bool
	const funcName = "/internal/storage/postgresql/CheckDateTime"

	dateValue := time.Date(date.Year, time.Month(date.Month), date.Day, date.Hours, date.Minutes, date.Seconds, 0, time.Local) // Преобразуйте в time.Time
	fmt.Println(dateValue.Format("2006-01-02 15:04:05"))
	query := `SELECT EXISTS (SELECT 1 FROM appointments WHERE event_time = $1)`

	_ = pg.db.QueryRow(query, dateValue).Scan(&exists)

	fmt.Println(exists)
	return nil, exists
}

func (pg *PostgresSqlx) NewAppointment(date types.Date, appoint types.Appointment) error {
	const funcName = "/internal/storage/postgresql/NewAppointment"
	query := `INSERT INTO appointments (firstname, midname, lastname, service, event_time, online) VALUES ($1, $2, $3, $4, $5, $6)`
	dateValue := time.Date(date.Year, time.Month(date.Month), date.Day, date.Hours, date.Minutes, date.Seconds, 0, time.Local)
	dateValue.Format("2006-01-02 15:04:05")
	_, err := pg.db.Exec(query, appoint.FirstName, appoint.MidName, appoint.LastName, appoint.Service, dateValue, appoint.Online)
	if err != nil {
		log.Printf("Error appending new appointment into database: %v, %s", err, funcName)
	}
	return err
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
