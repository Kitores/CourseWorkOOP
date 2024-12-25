package types

import "time"

type Date struct {
	Year    int
	Month   int
	Day     int
	Hours   int
	Minutes int
	Seconds int
}
type Date2 struct {
	date time.Time
}

type Appointment struct {
	Id        int32
	FirstName string
	MidName   string
	LastName  string
	Datetime  time.Time
	Service   string
	Online    bool
}
