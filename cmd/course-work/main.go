package main

import (
	"CourseWork/internal/config"
	"CourseWork/internal/http-server/handlers/addAppointment"
	"CourseWork/internal/http-server/handlers/checkDate"
	"CourseWork/internal/http-server/handlers/getAppointments"
	"CourseWork/internal/setupLogger"
	"CourseWork/internal/storage/postgresql"
	"CourseWork/lib/logger/sl"
	"context"
	"fmt"
	"github.com/go-chi/chi"
	"github.com/go-chi/chi/middleware"
	"log/slog"
	"net/http"
	"os"
)

func main() {
	cfg := config.MustLoad()
	fmt.Printf("%#v\n", cfg)

	log := setupLogger.SetupLogger(cfg.Env)
	log.Info("starting server", slog.String("env", cfg.Env))
	log.Debug("Debug logging enabled")

	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=%s", cfg.Host, cfg.Port, cfg.Userdb, cfg.DBPassword, cfg.DBname, cfg.SSLmode)
	storage, err := postgresql.NewPG(connStr)
	fmt.Println(storage, err)
	if err != nil {
		os.Exit(1)
	}

	router := chi.NewRouter()
	router.Use(middleware.Logger)
	router.Use(middleware.Recoverer)

	router.Get("/checkDate", checkDate.New(log, storage))
	//
	router.Post("/newAppointment", addAppointment.New(log, storage))
	//
	router.Get("/getAppointments", getAppointments.New(log, storage))
	//
	log.Info("starting server", slog.String("address", cfg.Address))
	//
	srv := &http.Server{
		Addr:         cfg.Address,
		Handler:      router,
		ReadTimeout:  cfg.HTTPServer.TimeOut,
		WriteTimeout: cfg.HTTPServer.TimeOut,
		IdleTimeout:  cfg.HTTPServer.IdleTimeOut,
	}
	if err := srv.ListenAndServe(); err != nil {
		log.Error("Failed to start server", sl.Err(err))
	}
	log.Error("failed to start server", sl.Err(srv.Shutdown(context.Background())))

}
