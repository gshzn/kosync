package main

import (
	"context"
	"net/http"

	"github.com/wailsapp/wails/v2/pkg/runtime"
)

type App struct {
	ctx        context.Context
	httpServer *http.Server
}

func NewApp() *App {
	return &App{}
}

func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
	mux := http.NewServeMux()
	mux.HandleFunc("/callback", a.handleCallback)
	a.httpServer = &http.Server{
		Addr:    "127.0.0.1:45289",
		Handler: mux,
	}
	go func() {
		if err := a.httpServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			runtime.LogErrorf(ctx, "local auth server: %v", err)
		}
	}()
}

func (a *App) shutdown(ctx context.Context) {
	if a.httpServer != nil {
		_ = a.httpServer.Shutdown(ctx)
	}
}

func (a *App) handleCallback(w http.ResponseWriter, r *http.Request) {
	accessToken := r.URL.Query().Get("access_token")
	refreshToken := r.URL.Query().Get("refresh_token")
	if accessToken == "" || refreshToken == "" {
		http.Error(w, "missing access_token or refresh_token", http.StatusBadRequest)
		return
	}
	runtime.EventsEmit(a.ctx, "auth-complete", map[string]string{
		"access_token":  accessToken,
		"refresh_token": refreshToken,
	})
	runtime.WindowShow(a.ctx)
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	_, _ = w.Write([]byte(`<!DOCTYPE html><html><head><title>Kosync</title></head><body style="font-family:system-ui;text-align:center;padding:4rem"><h2>Authentication successful</h2><p>You can close this tab and return to the installer.</p></body></html>`))
}
