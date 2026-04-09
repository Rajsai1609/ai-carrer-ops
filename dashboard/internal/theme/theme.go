package theme

import "github.com/charmbracelet/lipgloss"

// Theme holds all styled components used by the TUI.
type Theme struct {
	Base       lipgloss.Style
	Header     lipgloss.Style
	Title      lipgloss.Style
	Subtitle   lipgloss.Style
	Body       lipgloss.Style
	Muted      lipgloss.Style
	Accent     lipgloss.Style
	Success    lipgloss.Style
	Warning    lipgloss.Style
	Danger     lipgloss.Style
	Info       lipgloss.Style
	Border     lipgloss.Style
	Selected   lipgloss.Style
	Table      lipgloss.Style
	StatusPill func(status string) lipgloss.Style
}

// Default returns the default Catppuccin Mocha theme.
func Default() Theme {
	t := Theme{}

	t.Base = lipgloss.NewStyle().
		Background(lipgloss.Color(CatppuccinBase)).
		Foreground(lipgloss.Color(CatppuccinText))

	t.Header = lipgloss.NewStyle().
		Background(lipgloss.Color(CatppuccinMantle)).
		Foreground(lipgloss.Color(CatppuccinLavender)).
		Bold(true).
		Padding(0, 2)

	t.Title = lipgloss.NewStyle().
		Foreground(lipgloss.Color(CatppuccinMauve)).
		Bold(true)

	t.Subtitle = lipgloss.NewStyle().
		Foreground(lipgloss.Color(CatppuccinLavender))

	t.Body = lipgloss.NewStyle().
		Foreground(lipgloss.Color(CatppuccinText))

	t.Muted = lipgloss.NewStyle().
		Foreground(lipgloss.Color(CatppuccinOverlay1))

	t.Accent = lipgloss.NewStyle().
		Foreground(lipgloss.Color(CatppuccinBlue))

	t.Success = lipgloss.NewStyle().
		Foreground(lipgloss.Color(CatppuccinGreen))

	t.Warning = lipgloss.NewStyle().
		Foreground(lipgloss.Color(CatppuccinYellow))

	t.Danger = lipgloss.NewStyle().
		Foreground(lipgloss.Color(CatppuccinRed))

	t.Info = lipgloss.NewStyle().
		Foreground(lipgloss.Color(CatppuccinSky))

	t.Border = lipgloss.NewStyle().
		Border(lipgloss.RoundedBorder()).
		BorderForeground(lipgloss.Color(CatppuccinSurface1)).
		Padding(0, 1)

	t.Selected = lipgloss.NewStyle().
		Background(lipgloss.Color(CatppuccinSurface0)).
		Foreground(lipgloss.Color(CatppuccinLavender)).
		Bold(true)

	t.Table = lipgloss.NewStyle().
		Border(lipgloss.NormalBorder()).
		BorderForeground(lipgloss.Color(CatppuccinSurface1))

	t.StatusPill = func(status string) lipgloss.Style {
		base := lipgloss.NewStyle().Bold(true).Padding(0, 1)
		switch status {
		case "Applied":
			return base.Foreground(lipgloss.Color(CatppuccinBlue))
		case "Screening":
			return base.Foreground(lipgloss.Color(CatppuccinSky))
		case "Interview":
			return base.Foreground(lipgloss.Color(CatppuccinYellow))
		case "Offer":
			return base.Foreground(lipgloss.Color(CatppuccinGreen))
		case "Rejected":
			return base.Foreground(lipgloss.Color(CatppuccinRed))
		case "Withdrawn":
			return base.Foreground(lipgloss.Color(CatppuccinOverlay1))
		case "Ghosted":
			return base.Foreground(lipgloss.Color(CatppuccinMaroon))
		case "Pipeline":
			return base.Foreground(lipgloss.Color(CatppuccinMauve))
		default:
			return base.Foreground(lipgloss.Color(CatppuccinText))
		}
	}

	return t
}
