package addAppointment

import (
	resp "CourseWork/internal/lib/api/response"
	"CourseWork/lib/logger/sl"
	"CourseWork/lib/types"
	"github.com/go-chi/render"
	"log/slog"
	"net/http"
)

type Request struct {
	Year      int    `json:"year"`
	Month     int    `json:"month"`
	Day       int    `json:"day"`
	Hours     int    `json:"hours"`
	Minutes   int    `json:"minutes"`
	Seconds   int    `json:"seconds"`
	FirstName string `json:"firstName"`
	MidName   string `json:"midName"`
	LastName  string `json:"lastName"`
	Service   string `json:"service"`
	Online    bool   `json:"online"`
}
type Response struct {
	resp.Response
}

type AppointmentCreator interface {
	NewAppointment(date types.Date, appoint types.Appointment) error
}

func New(log *slog.Logger, appointmentCreator AppointmentCreator) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		functionName := "handlers.addAppointment.New"
		log = log.With(slog.String("funcName", functionName))

		var req Request
		err := render.DecodeJSON(r.Body, &req)
		if err != nil {
			log.Error("failed to decode request body", sl.Err(err))
			render.JSON(w, r, resp.Error("failed to Decode request"))
			return
		}
		log.Info("Request body decoded", slog.Any("request", req))

		date := types.Date{
			Year:    req.Year,
			Month:   req.Month,
			Day:     req.Day,
			Hours:   req.Hours,
			Minutes: req.Minutes,
			Seconds: req.Seconds,
		}
		appoint := types.Appointment{
			FirstName: req.FirstName,
			MidName:   req.MidName,
			LastName:  req.LastName,
			Service:   req.Service,
			Online:    req.Online,
		}

		err = appointmentCreator.NewAppointment(date, appoint)
		if err != nil {
			log.Error("failed to create appointment", sl.Err(err))
		}
		render.JSON(w, r, Response{
			Response: resp.OK(),
		})
	}
}
