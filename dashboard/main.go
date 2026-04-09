package main

import (
	"fmt"
	"os"
	"path/filepath"
	"runtime"

	tea "github.com/charmbracelet/bubbletea"

	"career-ops-dashboard/internal/data"
	"career-ops-dashboard/internal/theme"
	"career-ops-dashboard/internal/ui/screens"
)

func main() {
	// Resolve project root (one level above dashboard/)
	execPath, err := os.Executable()
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: cannot resolve executable path: %v\n", err)
		os.Exit(1)
	}

	// During development (go run), use working directory
	projectRoot := filepath.Dir(filepath.Dir(execPath))
	if _, err := os.Stat(filepath.Join(projectRoot, "data")); os.IsNotExist(err) {
		// Fallback: walk up from cwd
		cwd, _ := os.Getwd()
		projectRoot = filepath.Dir(cwd)
	}

	// Allow override via environment
	if override := os.Getenv("CAREER_OPS_ROOT"); override != "" {
		projectRoot = override
	}

	// Load applications
	apps, err := data.LoadApplications(projectRoot)
	if err != nil {
		if os.IsNotExist(err) {
			fmt.Fprintf(os.Stderr, "Note: data/applications.md not found at %s\n", projectRoot)
			fmt.Fprintf(os.Stderr, "Starting with empty pipeline. Create data/applications.md to populate.\n\n")
			apps = nil
		} else {
			fmt.Fprintf(os.Stderr, "warning: could not load applications: %v\n", err)
			apps = nil
		}
	}

	t := theme.Default()
	model := screens.NewPipelineModel(apps, t)

	// Configure Bubble Tea program
	opts := []tea.ProgramOption{tea.WithAltScreen()}
	if runtime.GOOS == "windows" {
		// Windows terminal mouse support
		opts = append(opts, tea.WithMouseCellMotion())
	}

	p := tea.NewProgram(model, opts...)
	if _, err := p.Run(); err != nil {
		fmt.Fprintf(os.Stderr, "error running dashboard: %v\n", err)
		os.Exit(1)
	}
}
