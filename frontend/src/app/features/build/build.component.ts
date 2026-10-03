import { ChangeDetectionStrategy, ChangeDetectorRef, Component, DestroyRef, OnInit, inject } from '@angular/core';

import { CommonModule } from '@angular/common';

import { ActivatedRoute, RouterLink } from '@angular/router';
import { interval, startWith, switchMap, takeWhile } from 'rxjs';

import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { ApiService } from '../../core/api.service';

import { AgentState, ApprovalGate, BlueprintUpdate, BuildStage, BuildState } from '../../shared/models/build.models';



interface AgentNode { name: string; icon: string; position: string; }



@Component({

  selector: 'app-build',

  standalone: true,

  imports: [CommonModule, RouterLink],
  templateUrl: './build.component.html',

  styleUrl: './build.component.scss',

  changeDetection: ChangeDetectionStrategy.OnPush,

})

export class BuildComponent implements OnInit {

  private readonly route = inject(ActivatedRoute);

  private readonly api = inject(ApiService);

  private readonly destroyRef = inject(DestroyRef);

  private readonly cdr = inject(ChangeDetectorRef);

  private hasStarted = false;



  build: BuildState | null = null;

  loadError: string | null = null;

  blueprintDraft: BlueprintUpdate | null = null;

  blueprintSecurityDraft = '';
  blueprintMessage: string | null = null;

  isSavingBlueprint = false;
  approvingGate: Exclude<ApprovalGate, null> | null = null;
  isRunningSecurityReview = false;
  isPreparingDeployment = false;
  isRefiningRequirements = false;
  refineMessage: string | null = null;

  readonly stages = ['Understand', 'Design', 'Forge', 'Prove', 'Release'] as const;

  readonly agentNodes: AgentNode[] = [

    { name: 'Spec Agent', icon: 'S', position: 'node-top' },

    { name: 'Architecture Agent', icon: 'A', position: 'node-right-top' },

    { name: 'Coder Agent', icon: 'C', position: 'node-right-bottom' },

    { name: 'Critic Agent', icon: 'Q', position: 'node-bottom' },

    { name: 'Security Reviewer', icon: 'S', position: 'node-left-bottom' },

    { name: 'Skill Agent', icon: 'K', position: 'node-left-top' },

    { name: 'Deployer Agent', icon: 'D', position: 'node-deployer' },

  ];

  ngOnInit(): void {

  const buildId = this.route.snapshot.paramMap.get('id');

  if (!buildId) return;



  interval(1000)

    .pipe(

      startWith(0),

      switchMap(() => this.api.getBuild(buildId)),



      takeWhile(
        (build) =>
          build.status !== 'Awaiting Approval' &&
          build.status !== 'Blocked' &&
          build.stage !== 'Error',
        true,

      ),



      takeUntilDestroyed(this.destroyRef),

    )

    .subscribe({

      next: (build) => {

        this.build = build;
        if (build.blueprint && !this.blueprintDraft) {

          this.blueprintDraft = this.toBlueprintUpdate(build.blueprint);

          this.blueprintSecurityDraft = build.blueprint.security.join('\n');

        }



  this.cdr.markForCheck();



  if (build.stage === 'Draft' && !this.hasStarted) {

    this.hasStarted = true;

    this.api.startBuild(build.id).subscribe({

      error: (error: unknown) => {

        console.error('Unable to start build', error);

        this.loadError = this.describeError(error, 'Unable to start analysis.');

        this.cdr.markForCheck();

      },

    });

  }

},

      error: (error: unknown) => {

        console.error('Unable to load build', error);

        this.loadError = this.describeError(error, 'Unable to load this build.');
        this.cdr.markForCheck();

      },

    });

}



  get stageIndex(): number {

    const stage = this.build?.stage;

    const indexByStage: Record<BuildStage, number> = {

      Draft: 0,

      Understand: 0,

      Design: 1,

      Forge: 2,

      Prove: 3,

      Release: 4,

      Replay: 4,

      Error: 0,

    };

    return stage ? indexByStage[stage] : 0;

  }



  get stageTitle(): string {

    const titles: Record<BuildStage, string> = {

      Draft: 'Preparing the Forge',

      Understand: 'Spec Agent Workspace',

      Design: 'Solution Blueprint',

      Forge: 'Code Forge',

      Prove: 'Proof Lab',

      Release: 'Release Gate',

      Replay: 'Run Replay & Observability',

      Error: 'Forge stopped',

    };

    return this.build ? titles[this.build.stage] : titles.Draft;

  }



  get stageSubtitle(): string {

    const subtitles: Record<BuildStage, string> = {

      Draft: 'The Orchestrator is preparing the governed workflow.',

      Understand: 'Understand, extract and refine requirements with the Spec Agent.',

      Design: 'Translate approved requirements into an implementation blueprint.',

      Forge: 'Generate application code, tests and reusable engineering skills.',

      Prove: 'Review generated source and show which sandbox checks still need to run.',
      Release: 'Complete security gates and obtain human approval before deployment.',

      Replay: 'Review the complete execution timeline, audit trail and AgentOps metrics.',

      Error: 'Review the failure and restart the Forge after the input is corrected.',

    };

    return this.build ? subtitles[this.build.stage] : subtitles.Draft;

  }



  get activeAgent(): AgentState | undefined {

    return this.build?.agents.find((agent) => agent.status === 'Running');

  }



  get sourceLabel(): string {

    const labels: Record<string, string> = {

      jira: 'Jira Ticket',

      openapi: 'OpenAPI / Specification',

      architecture: 'Architecture Document',

      upload: 'Engineering Documents',

      usecase: 'Use Case',

      requirement: 'Requirement',

    };

    return this.build ? labels[this.build.sourceType] ?? this.build.sourceType : '';

  }



  agentStatus(name: string): string {

    return this.build?.agents.find((agent) => agent.name === name)?.status ?? 'Ready';

  }



  agentDetail(name: string): string {

    return this.build?.agents.find((agent) => agent.name === name)?.detail ?? '';

  }



  approve(gate: Exclude<ApprovalGate, null>): void {
    if (!this.build || this.approvingGate || this.build.approvalGate !== gate) return;

    this.approvingGate = gate;
    this.loadError = null;
    this.cdr.markForCheck();

    this.api.approve(this.build.id, gate).subscribe({
      next: (build) => {
        this.build = build;
        this.loadError = null;
        this.approvingGate = null;
        if (build.blueprint && !this.blueprintDraft) {
          this.blueprintDraft = this.toBlueprintUpdate(build.blueprint);
          this.blueprintSecurityDraft = build.blueprint.security.join('\n');
        }
        if (build.status === 'Running') {
          this.approvingGate = gate;
          this.watchApprovalProgress(build.id);
        }
        this.cdr.markForCheck();
      },
      error: (error: unknown) => {
        console.error('Approval failed', error);
        // Approval can outlast the gateway's HTTP timeout while the backend
        // continues generating code. Reload the persisted build before
        // offering the user a retry, then follow it until the operation ends.
        this.api.getBuild(this.build!.id).subscribe({
          next: (latestBuild) => {
            this.build = latestBuild;
            const gateChanged = latestBuild.approvalGate !== gate;
            this.loadError = gateChanged
              ? `The ${gate} approval request was accepted, but the response timed out. The workspace state has been refreshed.`
              : this.describeError(error, 'Approval failed.');
            this.approvingGate = latestBuild.status === 'Running' ? gate : null;
            this.cdr.markForCheck();

            if (latestBuild.status === 'Running') this.watchApprovalProgress(latestBuild.id);
          },
          error: (refreshError: unknown) => {
            this.approvingGate = null;
            this.loadError = this.describeError(refreshError, 'Approval response timed out and workspace status could not be refreshed.');
            this.cdr.markForCheck();
          },
        });
      },
    });
  }

  get artifactsZipUrl(): string | null {
    return this.build?.proof?.artifacts && Object.keys(this.build.proof.artifacts).length
      ? `/api/builds/${encodeURIComponent(this.build.id)}/artifacts.zip?rev=${this.build.audit.length}`
      : null;
  }

  refine(): void {

    if (!this.build || this.isRefiningRequirements) return;

    this.isRefiningRequirements = true;
    this.refineMessage = null;
    this.loadError = null;
    this.cdr.markForCheck();

    this.api.refine(

      this.build.id,

      'Please add explicit input validation, authentication and retry/error-handling requirements.',

    ).subscribe({
      next: (build) => {
        this.build = build;
        this.isRefiningRequirements = false;
        this.refineMessage = 'Requirements refined. Review the updated specification before approving.';
        this.cdr.markForCheck();
      },
      error: (error: unknown) => {
        this.isRefiningRequirements = false;
        this.loadError = this.describeError(error, 'Requirements could not be refined.');
        this.cdr.markForCheck();
      },
    });

  }

  runSecurityReview(): void {
    if (!this.build || this.isRunningSecurityReview) return;
    this.isRunningSecurityReview = true;
    this.api.runSecurityReview(this.build.id).subscribe({
      next: (build) => {
        this.build = build;
        this.isRunningSecurityReview = false;
        this.cdr.markForCheck();
      },
      error: (error: unknown) => {
        this.loadError = this.describeError(error, 'Security review could not be completed.');
        this.isRunningSecurityReview = false;
        this.cdr.markForCheck();
      },
    });
  }

  prepareDeployment(): void {
    if (!this.build || this.isPreparingDeployment) return;
    this.isPreparingDeployment = true;
    this.api.prepareDeployment(this.build.id).subscribe({
      next: (build) => {
        this.build = build;
        this.isPreparingDeployment = false;
        this.cdr.markForCheck();
      },
      error: (error: unknown) => {
        this.loadError = this.describeError(error, 'Deployment preflight could not be completed.');
        this.isPreparingDeployment = false;
        this.cdr.markForCheck();
      },
    });
  }

  private watchApprovalProgress(buildId: string): void {
    interval(1500)
      .pipe(
        startWith(0),
        switchMap(() => this.api.getBuild(buildId)),
        takeWhile((updatedBuild) => updatedBuild.status === 'Running', true),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (updatedBuild) => {
          this.build = updatedBuild;
          if (updatedBuild.status !== 'Running') {
            this.approvingGate = null;
            this.loadError = updatedBuild.status === 'Failed'
              ? updatedBuild.error ?? 'The approved workflow failed. Review the build timeline for details.'
              : null;
          }
          this.cdr.markForCheck();
        },
        error: (refreshError: unknown) => {
          this.approvingGate = null;
          this.loadError = this.describeError(refreshError, 'Unable to refresh the approval status.');
          this.cdr.markForCheck();
        },
      });
  }


  updateBlueprintField(field: Exclude<keyof BlueprintUpdate, 'security'>, event: Event): void {

    const target = event.target;

    if (!this.blueprintDraft || !(target instanceof HTMLInputElement)) return;

    this.blueprintMessage = null;
    this.blueprintDraft = { ...this.blueprintDraft, [field]: target.value };

  }



  saveBlueprint(approveAfterSave = false): void {

    if (!this.build || this.isSavingBlueprint || this.approvingGate) return;

    const draft = this.blueprintDraft ?? (this.build.blueprint ? this.toBlueprintUpdate(this.build.blueprint) : null);
    if (!draft) {
      this.loadError = 'The solution blueprint is still loading. Refresh the workspace and try again.';
      this.cdr.markForCheck();
      return;
    }

    const request: BlueprintUpdate = {

      ...draft,

      security: this.blueprintSecurityDraft.split('\n').map((item) => item.trim()).filter(Boolean),

    };

    const unchanged = this.build.blueprint &&
      JSON.stringify(request) === JSON.stringify(this.toBlueprintUpdate(this.build.blueprint));

    // Avoid model/HTTP work if a save request would not change anything.
    if (unchanged) {
      if (approveAfterSave) this.approve('blueprint');
      else {
        this.blueprintMessage = 'These blueprint choices are already saved.';
        this.cdr.markForCheck();
      }
      return;
    }

    this.isSavingBlueprint = true;
    this.blueprintMessage = approveAfterSave ? 'Saving choices before approval…' : 'Saving blueprint choices…';
    this.loadError = null;

    this.api.updateBlueprint(this.build.id, request).subscribe({

      next: (build) => {

        this.build = build;

        this.blueprintDraft = this.toBlueprintUpdate(build.blueprint!);

        this.blueprintSecurityDraft = build.blueprint!.security.join('\n');

        this.isSavingBlueprint = false;
        this.blueprintMessage = approveAfterSave
          ? 'Blueprint saved. Starting Agent 3…'
          : 'Blueprint choices saved.';

        this.cdr.markForCheck();

        if (approveAfterSave) this.approve('blueprint');

      },

      error: (error: unknown) => {

        this.isSavingBlueprint = false;
        this.blueprintMessage = null;

        this.loadError = this.describeError(error, 'Unable to save blueprint choices.');

        this.cdr.markForCheck();

      },

    });

  }



  private toBlueprintUpdate(blueprint: NonNullable<BuildState['blueprint']>): BlueprintUpdate {

    return {

      application: blueprint.application,

      frontend: blueprint.frontend,

      backend: blueprint.backend,

      data: blueprint.data,

      storage: blueprint.storage,

      messaging: blueprint.messaging,

      identity: blueprint.identity,

      deployment: blueprint.deployment,

      security: [...blueprint.security],

    };

  }



  private describeError(error: unknown, fallback: string): string {

    if (typeof error === 'object' && error !== null && 'message' in error) {

      if ('error' in error) {

        const body = (error as { error?: unknown }).error;

        if (typeof body === 'object' && body !== null && 'detail' in body) {

          const detail = (body as { detail?: unknown }).detail;

          if (typeof detail === 'string' && detail.trim()) return detail;

        }

      }

      const message = (error as { message?: unknown }).message;

      if (typeof message === 'string' && message.trim()) return message;

    }

    return fallback;

  }

}
