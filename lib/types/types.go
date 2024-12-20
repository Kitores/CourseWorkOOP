package types

type Date struct {
	Year    int
	Month   int
	Day     int
	Hours   int
	Minutes int
	Seconds int
}

type Appointment struct {
	FirstName string
	MidName   string
	LastName  string
	Service   string
	Online    bool
}
