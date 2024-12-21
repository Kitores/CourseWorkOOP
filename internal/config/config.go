package config

import (
	"github.com/ilyakaznacheev/cleanenv"
	"log"
	"os"
	"time"
)

type Config struct {
	Env        string `yaml:"env" env-default:"local"`
	HTTPServer `yaml:"http_server" env-required:"true"`
	Storage    `yaml:"storage" env-required:"true"`
}

type HTTPServer struct {
	Address     string        `yaml:"address"  env-default:"localhost:8080"`
	TimeOut     time.Duration `yaml:"timeout" env-default:"4s"`
	IdleTimeOut time.Duration `yaml:"idle_timeout" env-default:"60s"`
	User        string        `yaml:"user" env-required:"true"`
	Password    string        `yaml:"password" env-required:"true" env:"HTTP_SERVER_PASSWORD"`
}
type Storage struct {
	Host       string `yaml:"host" env-required:"true"`
	Port       string `yaml:"port" env-required:"true"`
	Userdb     string `yaml:"userdb" env-required:"true"`
	DBPassword string `yaml:"dbpassword" env-required:"true"`
	DBname     string `yaml:"dbname" env-required:"true"`
	SSLmode    string `yaml:"sslmode" env-required:"true"`
}

func MustLoad() *Config {
	//err := godotenv.Load("config.env")
	//if err != nil {
	//	log.Fatal("Error loading .env file")
	//}
	//configPath := os.Getenv("CONFIG_PATH")
	//if configPath == "" {
	//	log.Fatal("CONFIG_PATH environment variable not set")
	//}

	configPath := "config/local.yaml"

	// check if file exists
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		log.Fatalf("CONFIG_PATH file does not exist: %s", configPath)
	}

	var cfg Config
	if err := cleanenv.ReadConfig(configPath, &cfg); err != nil {
		log.Fatalf("Error reading config file %s: %s", configPath, err)
	}
	return &cfg
}
