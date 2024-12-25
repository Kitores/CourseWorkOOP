package addAppointment

import (
	resp "CourseWork/internal/lib/api/response"
	"CourseWork/lib/logger/sl"
	"CourseWork/lib/types"
	"github.com/go-chi/render"
	"log/slog"
	"net/http"
	"time"
)

type Request struct {
	Date      time.Time `json:"date"`
	FirstName string    `json:"firstName"`
	MidName   string    `json:"midName"`
	LastName  string    `json:"lastName"`
	Service   string    `json:"service"`
	Online    bool      `json:"online"`
}
type Response struct {
	resp.Response
}

type AppointmentCreator interface {
	NewAppointment(appoint types.Appointment) error
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

		appoint := types.Appointment{
			FirstName: req.FirstName,
			MidName:   req.MidName,
			LastName:  req.LastName,
			Datetime:  req.Date,
			Service:   req.Service,
			Online:    req.Online,
		}

		err = appointmentCreator.NewAppointment(appoint)
		if err != nil {
			log.Error("failed to create appointment", sl.Err(err))
		}
		render.JSON(w, r, Response{
			Response: resp.OK(),
		})
	}
}
