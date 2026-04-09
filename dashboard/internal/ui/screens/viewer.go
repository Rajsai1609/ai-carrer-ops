package screens

import (
	"fmt"
	"os"
	"strings"

	tea "github.com/charmbracelet/bubbletea"

	"career-ops-dashboard/internal/model"
	"career-ops-dashboard/internal/theme"
)

// ViewerModel displays a single application report.
type ViewerModel struct {
	app     model.CareerApplication
	theme   theme.Theme
	content string
	scroll  int
	width   int
	height  int
}

// NewViewerModel creates a viewer for a single application.
func NewViewerModel(app model.CareerApplication, t theme.Theme) ViewerModel {
	content := loadReportContent(app.Report)
	return ViewerModel{
		app:     app,
		theme:   t,
		content: content,
	}
}

func loadReportContent(reportPath string) string {
	if reportPath == "" || reportPath == "-" {
		return "No report file linked for this application."
	}
	data, err := os.ReadFile(reportPath)
	if err != nil {
		return fmt.Sprintf("Could not load report: %s\n\nError: %v", reportPath, err)
	}
	return string(data)
}

func (m ViewerModel) Init() tea.Cmd {
	return nil
}

func (m ViewerModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q", "esc", "ctrl+c":
			return m, tea.Quit
		case "up", "k":
			if m.scroll > 0 {
				m.scroll--
			}
		case "down", "j", " ":
			m.scroll++
		case "home", "g":
			m.scroll = 0
		}
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
	}
	return m, nil
}

func (m ViewerModel) View() string {
	if m.width == 0 {
		m.width = 120
		m.height = 40
	}

	t := m.theme
	var sb strings.Builder

	// Header
	title := fmt.Sprintf("  Report: %s — %s", m.app.Company, m.app.Role)
	sb.WriteString(t.Header.Width(m.width).Render(title))
	sb.WriteString("\n\n")

	// Metadata bar
	meta := fmt.Sprintf("  Status: %s  |  Score: %.1f  |  Grade: %s",
		string(m.app.Status), m.app.Score, m.app.Grade)
	sb.WriteString(t.Subtitle.Render(meta))
	sb.WriteString("\n\n")

	// Content
	lines := strings.Split(m.content, "\n")
	visible := m.height - 8
	if visible < 1 {
		visible = 20
	}

	start := m.scroll
	if start > len(lines) {
		start = len(lines)
	}
	end := start + visible
	if end > len(lines) {
		end = len(lines)
	}

	for _, line := range lines[start:end] {
		sb.WriteString(t.Body.Render("  "+line) + "\n")
	}

	// Footer
	scrollInfo := fmt.Sprintf("  Line %d/%d", start+1, len(lines))
	footer := t.Muted.Render(scrollInfo + "  •  ↑↓ scroll  q: back")
	sb.WriteString("\n" + footer)

	return sb.String()
}
