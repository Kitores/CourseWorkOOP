package checkDate

import (
	resp "CourseWork/internal/lib/api/response"
	"CourseWork/lib/logger/sl"
	"github.com/go-chi/render"
	"log/slog"
	"net/http"
	"time"
)

type Request struct {
	Date time.Time `json:"date"`
}
type Response struct {
	Exists bool `json:"exists"`
	resp.Response
}

type DateCheker interface {
	CheckDateTimeDB(date time.Time) (error, bool)
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

		var exists bool
		err, exists = dateCheker.CheckDateTimeDB(req.Date)

		if err != nil {
			log.Error("failed to check date", sl.Err(err))
			return
		}

		if exists {

		}
		render.JSON(w, r, Response{
			Exists:   exists,
			Response: resp.OK(),
		})
		//log.Info(fmt.Sprintf("Saved URL %s, row id %d", slog.String("url", url), id))
	}
}
