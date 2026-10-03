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

  isSavingBlueprint = false;
  approvingGate: Exclude<ApprovalGate, null> | null = null;
  isRefiningArtifacts = false;
  artifactFeedback = '';
  artifactMessage: string | null = null;
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

get codeFiles(): string[] {
    return this.build?.proof?.files ?? [];
  }

  get generatedCode(): string {
    const artifacts = this.build?.proof?.artifacts;
    return (this.selectedArtifactPath && artifacts?.[this.selectedArtifactPath]) || 'No generated source file selected.';
  }

  selectedArtifactPath = '';


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
        this.selectFirstArtifact(build);
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
        this.selectFirstArtifact(build);
        if (build.blueprint && !this.blueprintDraft) {
          this.blueprintDraft = this.toBlueprintUpdate(build.blueprint);
          this.blueprintSecurityDraft = build.blueprint.security.join('\n');
        }
        this.cdr.markForCheck();
      },
      error: (error: unknown) => {
        console.error('Approval failed', error);
        this.approvingGate = null;
        this.loadError = this.describeError(error, 'Approval failed.');
        this.cdr.markForCheck();
      },
    });
  }

  get artifactsZipUrl(): string | null {
    return this.build?.proof?.artifacts && Object.keys(this.build.proof.artifacts).length
      ? `/api/builds/${encodeURIComponent(this.build.id)}/artifacts.zip?rev=${this.build.audit.length}`
      : null;
  }

  get previewUrl(): string | null {
    // The backend can build a requirements-based visual fallback when the
    // Coder Agent omits the optional standalone preview file.
    return this.build?.proof?.artifacts && Object.keys(this.build.proof.artifacts).length > 0
      ? `/api/builds/${encodeURIComponent(this.build.id)}/preview?rev=${this.build.audit.length}`
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

  requestArtifactRevision(): void {
    const feedback = this.artifactFeedback.trim();
    if (!this.build || !feedback || this.isRefiningArtifacts || this.approvingGate) return;

    this.isRefiningArtifacts = true;
    this.artifactMessage = null;
    this.loadError = null;
    this.cdr.markForCheck();
    this.api.refineArtifacts(this.build.id, feedback).subscribe({
      next: (build) => {
        this.build = build;
        this.selectFirstArtifact(build);
        this.artifactFeedback = '';
        this.artifactMessage = 'Updated files are ready. Review the preview and ZIP again before continuing.';
        this.isRefiningArtifacts = false;
        this.cdr.markForCheck();
      },
      error: (error: unknown) => {
        this.loadError = this.describeError(error, 'The generated files could not be revised.');
        this.isRefiningArtifacts = false;
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

  selectArtifact(path: string): void {
    this.selectedArtifactPath = path;
  }

  private selectFirstArtifact(build: BuildState): void {
    const files = build.proof?.files ?? [];
    if (files.length && !files.includes(this.selectedArtifactPath)) {
      this.selectedArtifactPath = files[0];
    }
  }


  updateBlueprintField(field: Exclude<keyof BlueprintUpdate, 'security'>, event: Event): void {

    const target = event.target;

    if (!this.blueprintDraft || !(target instanceof HTMLInputElement)) return;

    this.blueprintDraft = { ...this.blueprintDraft, [field]: target.value };

  }



  saveBlueprint(approveAfterSave = false): void {

    if (!this.build || !this.blueprintDraft || this.isSavingBlueprint || this.approvingGate) return;

    const request: BlueprintUpdate = {

      ...this.blueprintDraft,

      security: this.blueprintSecurityDraft.split('\n').map((item) => item.trim()).filter(Boolean),

    };

    this.isSavingBlueprint = true;

    this.api.updateBlueprint(this.build.id, request).subscribe({

      next: (build) => {

        this.build = build;

        this.blueprintDraft = this.toBlueprintUpdate(build.blueprint!);

        this.blueprintSecurityDraft = build.blueprint!.security.join('\n');

        this.isSavingBlueprint = false;

        this.cdr.markForCheck();

        if (approveAfterSave) this.approve('blueprint');

      },

      error: (error: unknown) => {

        this.isSavingBlueprint = false;

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
