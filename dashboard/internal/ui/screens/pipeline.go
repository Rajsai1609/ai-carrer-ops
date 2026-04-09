package screens

import (
	"fmt"
	"strings"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"

	"career-ops-dashboard/internal/model"
	"career-ops-dashboard/internal/theme"
)

// PipelineModel is the main pipeline view screen.
type PipelineModel struct {
	apps     []model.CareerApplication
	metrics  model.PipelineMetrics
	theme    theme.Theme
	cursor   int
	width    int
	height   int
	selected *model.CareerApplication
}

// NewPipelineModel creates a new pipeline screen model.
func NewPipelineModel(apps []model.CareerApplication, t theme.Theme) PipelineModel {
	return PipelineModel{
		apps:    apps,
		metrics: model.ComputeMetrics(apps),
		theme:   t,
	}
}

func (m PipelineModel) Init() tea.Cmd {
	return nil
}

func (m PipelineModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q", "ctrl+c":
			return m, tea.Quit
		case "up", "k":
			if m.cursor > 0 {
				m.cursor--
			}
		case "down", "j":
			if m.cursor < len(m.apps)-1 {
				m.cursor++
			}
		case "enter":
			if len(m.apps) > 0 {
				a := m.apps[m.cursor]
				m.selected = &a
			}
		case "esc":
			m.selected = nil
		}
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
	}
	return m, nil
}

func (m PipelineModel) View() string {
	if m.width == 0 {
		m.width = 120
		m.height = 40
	}

	var sb strings.Builder

	// Header
	header := m.theme.Header.Width(m.width).Render(
		fmt.Sprintf("  Career-Ops Pipeline Dashboard  •  %d Applications", m.metrics.Total),
	)
	sb.WriteString(header + "\n\n")

	// Metrics bar
	sb.WriteString(m.renderMetrics())
	sb.WriteString("\n\n")

	// Table
	sb.WriteString(m.renderTable())
	sb.WriteString("\n")

	// Footer
	footer := m.theme.Muted.Render("  ↑↓ navigate  enter: detail  q: quit")
	sb.WriteString(footer)

	return sb.String()
}

func (m PipelineModel) renderMetrics() string {
	t := m.theme
	pills := []string{
		t.Info.Render(fmt.Sprintf("Applied: %d", m.metrics.Applied)),
		t.Accent.Render(fmt.Sprintf("Screening: %d", m.metrics.Screening)),
		t.Warning.Render(fmt.Sprintf("Interview: %d", m.metrics.Interview)),
		t.Success.Render(fmt.Sprintf("Offer: %d", m.metrics.Offer)),
		t.Danger.Render(fmt.Sprintf("Rejected: %d", m.metrics.Rejected)),
		t.Muted.Render(fmt.Sprintf("Ghosted: %d", m.metrics.Ghosted)),
		t.Muted.Render(fmt.Sprintf("Withdrawn: %d", m.metrics.Withdrawn)),
	}

	stats := []string{
		t.Subtitle.Render(fmt.Sprintf("Response Rate: %.1f%%", m.metrics.ResponseRate)),
		t.Subtitle.Render(fmt.Sprintf("Offer Rate: %.1f%%", m.metrics.OfferRate)),
		t.Subtitle.Render(fmt.Sprintf("Avg Score: %.1f", m.metrics.AvgScore)),
	}

	row1 := "  " + strings.Join(pills, "  ")
	row2 := "  " + strings.Join(stats, "  •  ")

	return row1 + "\n" + row2
}

func (m PipelineModel) renderTable() string {
	t := m.theme

	colWidths := []int{4, 12, 22, 28, 7, 12, 8}
	headers := []string{"#", "Date", "Company", "Role", "Score", "Status", "Grade"}

	headerCells := make([]string, len(headers))
	for i, h := range headers {
		headerCells[i] = t.Title.Width(colWidths[i]).Render(h)
	}
	headerRow := "  " + strings.Join(headerCells, " ")

	sep := "  " + strings.Repeat("─", sum(colWidths)+len(colWidths)*1)

	var rows []string
	rows = append(rows, headerRow)
	rows = append(rows, t.Muted.Render(sep))

	for i, app := range m.apps {
		dateStr := ""
		if !app.Date.IsZero() {
			dateStr = app.Date.Format("2006-01-02")
		}

		scoreStr := "-"
		if app.Score > 0 {
			scoreStr = fmt.Sprintf("%.1f", app.Score)
		}

		cells := []string{
			fmt.Sprintf("%*d", colWidths[0], app.Number),
			padRight(dateStr, colWidths[1]),
			padRight(truncate(app.Company, colWidths[2]-1), colWidths[2]),
			padRight(truncate(app.Role, colWidths[3]-1), colWidths[3]),
			padRight(scoreStr, colWidths[4]),
			t.StatusPill(string(app.Status)).Width(colWidths[5]).Render(string(app.Status)),
			padRight(app.Grade, colWidths[6]),
		}

		row := "  " + strings.Join(cells, " ")

		if i == m.cursor {
			row = t.Selected.Render(row)
		}
		rows = append(rows, row)
	}

	if len(m.apps) == 0 {
		rows = append(rows, "\n"+t.Muted.Render("  No applications found. Add entries to data/applications.md"))
	}

	return strings.Join(rows, "\n")
}

// statusColor returns a lipgloss color for a given status.
func statusColor(s model.Status) lipgloss.Color {
	switch s {
	case model.StatusApplied:
		return lipgloss.Color("#89b4fa")
	case model.StatusScreening:
		return lipgloss.Color("#89dceb")
	case model.StatusInterview:
		return lipgloss.Color("#f9e2af")
	case model.StatusOffer:
		return lipgloss.Color("#a6e3a1")
	case model.StatusRejected:
		return lipgloss.Color("#f38ba8")
	default:
		return lipgloss.Color("#9399b2")
	}
}

func padRight(s string, width int) string {
	if len(s) >= width {
		return s[:width]
	}
	return s + strings.Repeat(" ", width-len(s))
}

func truncate(s string, max int) string {
	if len(s) <= max {
		return s
	}
	return s[:max-1] + "…"
}

func sum(vals []int) int {
	total := 0
	for _, v := range vals {
		total += v
	}
	return total
}
