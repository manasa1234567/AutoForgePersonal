import { ChangeDetectionStrategy, ChangeDetectorRef, Component, DestroyRef, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ApiService } from '../../core/api.service';
import { AgentState, AuditEvent, BuildState } from '../../shared/models/build.models';

type WorkspacePage = 'agents' | 'skills' | 'knowledge' | 'run-history' | 'settings';

interface AgentCard {
  name: string;
  role: string;
  description: string;
  state: AgentState['status'] | 'Not run';
  activity: string;
  buildCount: number;
}

interface HistoryRow {
  buildId: string;
  title: string;
  event: AuditEvent;
}

@Component({
  selector: 'app-workspace',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './workspace.component.html',
  styleUrl: './workspace.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  readonly page: WorkspacePage = this.route.snapshot.data['workspacePage'] as WorkspacePage;
  readonly titles: Record<WorkspacePage, { title: string; intro: string; kicker: string }> = {
    agents: { title: 'Agents', intro: 'See the specialists in the workflow and their latest recorded activity.', kicker: 'WORKFLOW' },
    skills: { title: 'Skills', intro: 'Review skill proposals produced by builds and their approval state.', kicker: 'KNOWLEDGE' },
    knowledge: { title: 'Knowledge', intro: 'Find the engineering inputs attached to your builds.', kicker: 'SOURCES' },
    'run-history': { title: 'Run History', intro: 'Trace workflow events, approvals, and outcomes across builds.', kicker: 'AUDIT' },
    settings: { title: 'Settings', intro: 'Manage local workspace preferences and review integration setup.', kicker: 'WORKSPACE' },
  };

  builds: BuildState[] = [];
  loading = true;
  errorMessage = '';
  query = '';
  workspaceName = localStorage.getItem('autoforge.workspaceName') || 'AutoForge';
  saved = false;

  private readonly agentDescriptions: Record<string, string> = {
    'Spec Agent': 'Turns submitted intent into structured, reviewable requirements.',
    'Architecture Agent': 'Proposes an editable solution blueprint from approved requirements.',
    'Coder Agent': 'Generates project artifacts from the approved requirements and blueprint.',
    'Critic Agent': 'Reviews generated artifacts and reports checks, findings, and coverage.',
    'Skill Agent': 'Proposes reusable engineering skills based on workflow outcomes.',
    'Security Reviewer': 'Reviews security risks and policy requirements before release.',
    'Deployer Agent': 'Prepares and deploys an approved build to its target environment.',
  };

  ngOnInit(): void {
    this.api.getBuilds().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (builds) => {
        this.builds = builds;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.errorMessage = 'Unable to load workspace data. Confirm that the FastAPI service is running.';
        this.loading = false;
        this.cdr.markForCheck();
      },
    });
  }

  get agentCards(): AgentCard[] {
    const latestBuild = this.builds[0];
    const recorded = latestBuild?.agents ?? [];
    const names = new Set([...Object.keys(this.agentDescriptions), ...recorded.map((agent) => agent.name)]);
    return [...names].map((name) => {
      const current = recorded.find((agent) => agent.name === name);
      const count = this.builds.filter((build) => build.agents.some((agent) => agent.name === name)).length;
      return {
        name,
        role: current?.role ?? name,
        description: this.agentDescriptions[name] ?? 'Specialized workflow agent.',
        state: current?.status ?? 'Not run',
        activity: current?.lastAction || current?.detail || (current ? 'Ready for its workflow stage.' : 'No recorded activity yet.'),
        buildCount: count,
      };
    });
  }

  get skillBuilds(): BuildState[] {
    return this.builds.filter((build) => !!build.skillProposal && this.matches(
      `${build.skillProposal?.name} ${build.skillProposal?.reason} ${build.title}`,
    ));
  }

  get knowledgeBuilds(): BuildState[] {
    return this.builds.filter((build) => this.matches(
      `${build.title} ${build.sourceType} ${build.files.join(' ')} ${build.sourceText.slice(0, 500)}`,
    ));
  }

  get historyRows(): HistoryRow[] {
    return this.builds.flatMap((build) => [...build.audit].reverse().map((event) => ({
      buildId: build.id,
      title: build.title,
      event,
    }))).filter((row) => this.matches(`${row.title} ${row.event.stage} ${row.event.message} ${row.event.agent ?? ''}`));
  }

  setQuery(event: Event): void {
    this.query = (event.target as HTMLInputElement).value;
  }

  saveSettings(): void {
    const name = this.workspaceName.trim().slice(0, 60) || 'AutoForge';
    this.workspaceName = name;
    localStorage.setItem('autoforge.workspaceName', name);
    this.saved = true;
    window.setTimeout(() => {
      this.saved = false;
      this.cdr.markForCheck();
    }, 2500);
  }

  clearSettings(): void {
    localStorage.removeItem('autoforge.workspaceName');
    this.workspaceName = 'AutoForge';
    this.saved = true;
    window.setTimeout(() => {
      this.saved = false;
      this.cdr.markForCheck();
    }, 2500);
  }

  statusClass(status: string): string {
    return status.toLowerCase().replaceAll(' ', '-');
  }

  private matches(value: string): boolean {
    return !this.query.trim() || value.toLowerCase().includes(this.query.trim().toLowerCase());
  }
}
