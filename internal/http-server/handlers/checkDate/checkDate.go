package checkDate

import (
	resp "CourseWork/internal/lib/api/response"
	"CourseWork/lib/logger/sl"
	"CourseWork/lib/types"
	"github.com/go-chi/render"
	"log/slog"
	"net/http"
)

type Request struct {
	Year    int `json:"year"`
	Month   int `json:"month"`
	Day     int `json:"day"`
	Hours   int `json:"hours"`
	Minutes int `json:"minutes"`
	Seconds int `json:"seconds"`
}
type Response struct {
	Exists bool `json:"exists"`
	resp.Response
}

type DateCheker interface {
	CheckDateTimeDB(date types.Date) (error, bool)
}

func New(log *slog.Logger, dateCheker DateCheker) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		functionName := "handlers.checkDate.New"
		log = log.With(slog.String("funcName", functionName))

		var req Request
		err := render.DecodeJSON(r.Body, &req)
		if err != nil {
			log.Error("failed to decode request body", sl.Err(err))
			render.JSON(w, r, resp.Error("failed to Decode request"))
			return
		}
		log.Info("Request body decoded", slog.Any("request", req))

		var date = types.Date{
			Year:    req.Year,
			Month:   req.Month,
			Day:     req.Day,
			Hours:   req.Hours,
			Minutes: req.Minutes,
			Seconds: req.Seconds,
		}
		var exists bool
		err, exists = dateCheker.CheckDateTimeDB(date)

		if err != nil {
			log.Error("failed to check date", sl.Err(err))
			return
		}
		render.JSON(w, r, Response{
			Exists:   exists,
			Response: resp.OK(),
		})
		//log.Info(fmt.Sprintf("Saved URL %s, row id %d", slog.String("url", url), id))
	}
}
