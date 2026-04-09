package model

import "time"

// Status represents the canonical pipeline status of an application.
type Status string

const (
	StatusApplied    Status = "Applied"
	StatusScreening  Status = "Screening"
	StatusInterview  Status = "Interview"
	StatusOffer      Status = "Offer"
	StatusRejected   Status = "Rejected"
	StatusWithdrawn  Status = "Withdrawn"
	StatusGhosted    Status = "Ghosted"
	StatusPipeline   Status = "Pipeline"
)

// CareerApplication represents a single job application entry.
type CareerApplication struct {
	Number    int
	Date      time.Time
	Company   string
	Role      string
	Score     float64
	Grade     string
	Status    Status
	PDFPath   string
	Report    string
	Notes     string
}

// PipelineMetrics holds aggregate statistics for the current pipeline.
type PipelineMetrics struct {
	Total        int
	Applied      int
	Screening    int
	Interview    int
	Offer        int
	Rejected     int
	Withdrawn    int
	Ghosted      int
	Pipeline     int
	ResponseRate float64
	OfferRate    float64
	AvgScore     float64
	TopGrade     string
	RecentActivity []CareerApplication
}

// ComputeMetrics calculates pipeline metrics from a slice of applications.
func ComputeMetrics(apps []CareerApplication) PipelineMetrics {
	m := PipelineMetrics{Total: len(apps)}
	totalScore := 0.0
	scored := 0

	for _, a := range apps {
		switch a.Status {
		case StatusApplied:
			m.Applied++
		case StatusScreening:
			m.Screening++
		case StatusInterview:
			m.Interview++
		case StatusOffer:
			m.Offer++
		case StatusRejected:
			m.Rejected++
		case StatusWithdrawn:
			m.Withdrawn++
		case StatusGhosted:
			m.Ghosted++
		case StatusPipeline:
			m.Pipeline++
		}
		if a.Score > 0 {
			totalScore += a.Score
			scored++
		}
	}

	if m.Total > 0 {
		responded := m.Screening + m.Interview + m.Offer + m.Rejected
		m.ResponseRate = float64(responded) / float64(m.Total) * 100
		m.OfferRate = float64(m.Offer) / float64(m.Total) * 100
	}
	if scored > 0 {
		m.AvgScore = totalScore / float64(scored)
	}

	// Recent activity: last 5 entries
	if len(apps) > 5 {
		m.RecentActivity = apps[len(apps)-5:]
	} else {
		m.RecentActivity = apps
	}

	return m
}
