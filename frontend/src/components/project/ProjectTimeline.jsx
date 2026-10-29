const STATUS_STYLES = {
  completed: { dot: "bg-low", label: "Completed" },
  delayed: { dot: "bg-critical", label: "Delayed" },
  upcoming: { dot: "bg-accent", label: "Upcoming" },
  predicted: { dot: "bg-medium", label: "Predicted" },
};

export default function ProjectTimeline({ timeline }) {
  return (
    <ol className="relative space-y-4 border-l border-border pl-5">
      {timeline.events.map((event) => {
        const style = STATUS_STYLES[event.status] ?? STATUS_STYLES.upcoming;
        return (
          <li key={`${event.name}-${event.date}`} className="relative">
            <span className={`absolute -left-[26px] top-1 h-3 w-3 rounded-full ring-2 ring-surface ${style.dot}`} />
            <div className="flex flex-wrap items-baseline justify-between gap-2 text-sm">
              <span className="font-medium">{event.name}</span>
              <span className="text-xs text-text-muted">
                {event.date} · {style.label}
              </span>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
