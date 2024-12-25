package getAppointments

import (
	resp "CourseWork/internal/lib/api/response"
	"CourseWork/lib/logger/sl"
	"CourseWork/lib/types"
	"github.com/go-chi/render"
	"log/slog"
	"net/http"
)

type Request struct {
}
type Response struct {
	Appointments []types.Appointment `json:"appointments"`
	resp.Response
}

type AppointmentsGetter interface {
	GetAppointments() ([]types.Appointment, error)
}

func New(log *slog.Logger, appointmentGetter AppointmentsGetter) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		functionName := "handlers.getAppointment.New"
		log = log.With(slog.String("funcName", functionName))

		var req Request
		err := render.DecodeJSON(r.Body, &req)
		if err != nil {
			log.Error("failed to decode request body", sl.Err(err))
			render.JSON(w, r, resp.Error("failed to Decode request"))
			return
		}
		log.Info("Request body decoded", slog.Any("request", req))
		var appointments []types.Appointment
		appointments, err = appointmentGetter.GetAppointments()
		if err != nil {
			log.Error("failed to get appointments", sl.Err(err))
		}
		render.JSON(w, r, Response{
			Appointments: appointments,
			Response:     resp.OK(),
		})
	}
}
