import React from 'react';
import styles from './Dashboard.module.css';

// Example data for dashboard widgets (static, as no backend integration required)
const stats = [
  { id: 1, title: 'Users', value: '1,254', icon: '👥' },
  { id: 2, title: 'Revenue', value: '$43,215', icon: '💰' },
  { id: 3, title: 'Orders', value: '3,142', icon: '📦' },
  { id: 4, title: 'Tickets', value: '17', icon: '🎫' },
];

const recentActivities = [
  { id: 1, activity: 'New user registered: John Doe', time: '2 hrs ago' },
  { id: 2, activity: 'Order #1024 completed', time: '4 hrs ago' },
  { id: 3, activity: 'Support ticket #57 closed', time: '6 hrs ago' },
  { id: 4, activity: 'Revenue milestone reached', time: '1 day ago' },
];

export default function Dashboard() {
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>Dashboard</h1>
      </header>
      <section aria-label="Key statistics" className={styles.statsGrid}>
        {stats.map(({ id, title, value, icon }) => (
          <article key={id} className={styles.statCard} tabIndex={0} aria-label={`${title}: ${value}`}>
            <div className={styles.statIcon} aria-hidden="true">
              {icon}
            </div>
            <p className={styles.statTitle}>{title}</p>
            <p className={styles.statValue}>{value}</p>
          </article>
        ))}
      </section>
      <section className={styles.activitySection} aria-label="Recent activities">
        <h2 className={styles.activityTitle}>Recent Activities</h2>
        <ul className={styles.activityList}>
          {recentActivities.map(({ id, activity, time }) => (
            <li key={id} className={styles.activityItem} tabIndex={0}>
              <p className={styles.activityText}>{activity}</p>
              <time className={styles.activityTime}>{time}</time>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
