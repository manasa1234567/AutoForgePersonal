import { ChangeDetectionStrategy, ChangeDetectorRef, Component, DestroyRef, OnInit, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ApiService } from '../../core/api.service';
import { BuildState, SourceType } from '../../shared/models/build.models';

interface SourceOption {
  id: SourceType;
  icon: string;
  label: string;
  title: string;
  description: string;
  placeholder: string;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomeComponent implements OnInit {
  private readonly formBuilder = inject(FormBuilder);
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  readonly sourceOptions: SourceOption[] = [
    {
      id: 'jira',
      icon: 'J',
      label: 'Jira',
      title: 'Jira / Work Item',
      description: 'Bring an existing story, epic or requirement into the Forge.',
      placeholder: 'Enter a Jira key or paste the requirement details…',
    },
    {
      id: 'openapi',
      icon: '{}',
      label: 'OpenAPI',
      title: 'OpenAPI / Specification',
      description: 'Start from an API contract or engineering specification.',
      placeholder: 'Paste OpenAPI YAML/JSON or specification text…',
    },
    {
      id: 'architecture',
      icon: '⌁',
      label: 'Architecture',
      title: 'Architecture Document',
      description: 'Use architecture decisions, constraints and standards as input.',
      placeholder: 'Paste architecture notes or describe the target architecture…',
    },
    {
      id: 'upload',
      icon: '↑',
      label: 'Documents',
      title: 'Engineering Documents',
      description: 'Upload one or more approved engineering documents.',
      placeholder: 'Describe what the uploaded documents contain…',
    },
    {
      id: 'usecase',
      icon: '✦',
      label: 'Use Case',
      title: 'Business / Engineering Use Case',
      description: 'Describe the capability you want AutoForge to build.',
      placeholder: 'Example: Build a secure customer onboarding service with KYC verification…',
    },
    {
      id: 'requirement',
      icon: '≡',
      label: 'Requirement',
      title: 'Plain-language Requirement',
      description: 'Start with an engineering requirement written in your own words.',
      placeholder: 'Describe what you want AutoForge to build…',
    },
  ];

  recentBuilds: BuildState[] = [];
  recentBuildsLoading = true;
  recentBuildsUnavailable = false;

  selectedSource: SourceType = 'usecase';
  selectedFiles: string[] = [];
  private selectedFilePayloads: { name: string; contentBase64: string }[] = [];
  readingFiles = false;
  forgeOpen = false;
  submitting = false;
  errorMessage = '';

  readonly intakeForm = this.formBuilder.nonNullable.group({
    title: ['', [Validators.minLength(3), Validators.maxLength(160)]],
    sourceText: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(20000)]],
  });

  ngOnInit(): void {
    if (this.route.snapshot.data['openForge']) this.openForge();
    this.api.getBuilds().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (builds) => {
        this.recentBuilds = builds.slice(0, 4);
        this.recentBuildsLoading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.recentBuildsUnavailable = true;
        this.recentBuildsLoading = false;
        this.cdr.markForCheck();
      },
    });
  }

  statusClass(status: BuildState['status']): string {
    return status.toLowerCase().replaceAll(' ', '-');
  }

  lastActivity(build: BuildState): string {
    return build.audit.length ? build.audit[build.audit.length - 1].time : 'Just created';
  }

  get selectedOption(): SourceOption {
    return this.sourceOptions.find((option) => option.id === this.selectedSource) ?? this.sourceOptions[4];
  }

  openForge(): void {
    this.forgeOpen = true;
    this.errorMessage = '';
  }

  closeForge(): void {
    if (!this.submitting) {
      this.forgeOpen = false;
      if (this.route.snapshot.data['openForge']) this.router.navigate(['/']);
    }
  }

  selectSource(source: SourceType): void {
    this.selectedSource = source;
    this.errorMessage = '';

    // Each intake mode owns its own prompt. In particular, Jira starts from an
    // issue key; its title is supplied by Jira when the connector is enabled.
    const initialText: Record<SourceType, string> = {
      jira: '',
      openapi: '',
      architecture: '',
      upload: '',
      usecase: '',
      requirement: '',
    };
    this.intakeForm.controls.sourceText.setValue(initialText[source]);
    this.intakeForm.controls.sourceText.setValidators(source === 'jira'
      ? [Validators.required, Validators.minLength(3), Validators.maxLength(80)]
      : source === 'upload'
        ? []
        : [Validators.required, Validators.minLength(10), Validators.maxLength(20000)]);
    this.intakeForm.controls.sourceText.updateValueAndValidity();
    this.intakeForm.controls.sourceText.markAsPristine();
    this.intakeForm.controls.sourceText.markAsUntouched();
  }

  get isJiraSource(): boolean {
    return this.selectedSource === 'jira';
  }

  get titleError(): boolean {
    return this.intakeForm.controls.title.touched && this.intakeForm.controls.title.invalid;
  }

  get sourceTextError(): boolean {
    return this.selectedSource !== 'upload' && !this.hasCompatibleSourceFile
      && this.intakeForm.controls.sourceText.touched && this.intakeForm.controls.sourceText.invalid;
  }

  get hasCompatibleSourceFile(): boolean {
    if (this.selectedSource === 'openapi') {
      return this.selectedFilePayloads.some((file) => /\.(yaml|yml|json)$/i.test(file.name));
    }
    return this.selectedSource === 'architecture' && this.selectedFilePayloads.length > 0;
  }

  get filesError(): boolean {
    return this.selectedSource === 'upload' && this.intakeForm.controls.sourceText.touched && this.selectedFiles.length === 0;
  }

  async onFilesSelected(event: Event): Promise<void> {
    const input = event.target as HTMLInputElement;
    const files = Array.from(input.files ?? []);
    const allowedExtensions = new Set(['.yaml', '.yml', '.json', '.pdf', '.docx', '.txt', '.md']);
    const totalBytes = files.reduce((total, file) => total + file.size, 0);
    if (files.length > 10 || files.some((file) => !allowedExtensions.has(file.name.slice(file.name.lastIndexOf('.')).toLowerCase()))) {
      this.selectedFiles = [];
      this.selectedFilePayloads = [];
      this.errorMessage = 'Choose up to 10 supported files: OpenAPI YAML/JSON, PDF, DOCX, TXT or Markdown.';
      input.value = '';
      return;
    }
    if (totalBytes > 15_000_000) {
      this.selectedFiles = [];
      this.selectedFilePayloads = [];
      this.errorMessage = 'Keep the combined document size under 15 MB.';
      input.value = '';
      return;
    }

    this.errorMessage = '';
    this.readingFiles = true;
    try {
      const payloads = await Promise.all(files.map(async (file) => ({
        name: file.name,
        contentBase64: await this.toBase64(file),
      })));
      this.selectedFiles = files.map((file) => file.name);
      this.selectedFilePayloads = payloads;
    } catch {
      this.selectedFiles = [];
      this.selectedFilePayloads = [];
      this.errorMessage = 'Unable to read one or more selected documents.';
    } finally {
      this.readingFiles = false;
    }
  }

  private async toBase64(file: File): Promise<string> {
    const bytes = new Uint8Array(await file.arrayBuffer());
    let binary = '';
    for (let offset = 0; offset < bytes.length; offset += 0x8000) {
      binary += String.fromCharCode(...bytes.subarray(offset, offset + 0x8000));
    }
    return btoa(binary);
  }

  startForge(): void {
    const { title: enteredTitle, sourceText } = this.intakeForm.getRawValue();
    const titleIsValid = this.intakeForm.controls.title.valid;
    const sourceIsValid = this.selectedSource === 'upload'
      ? this.selectedFiles.length > 0
      : this.intakeForm.controls.sourceText.valid || this.hasCompatibleSourceFile;

    if (!titleIsValid || !sourceIsValid || this.submitting || this.readingFiles) {
      this.intakeForm.markAllAsTouched();
      this.intakeForm.controls.sourceText.markAsTouched();
      return;
    }

    this.submitting = true;
    this.errorMessage = '';

    const title = this.resolveBuildTitle(enteredTitle, sourceText);
    this.api.createBuild({
      title,
      sourceText,
      sourceType: this.selectedSource,
      files: this.selectedFiles,
      fileContents: this.selectedFilePayloads,
    }).subscribe({
      next: (build) => {
        this.router.navigate(['/build', build.id]);
      },
      error: () => {
        this.submitting = false;
        this.errorMessage = 'Unable to create the Forge. Confirm that the FastAPI service is running on port 8000.';
      },
    });
  }

  private resolveBuildTitle(enteredTitle: string, sourceText: string): string {
    const suppliedTitle = enteredTitle.trim();
    if (suppliedTitle) return suppliedTitle;

    if (this.selectedSource === 'jira') return `Jira ${sourceText.trim().toUpperCase()}`;
    if (this.selectedSource === 'upload') {
      return this.selectedFiles[0]?.replace(/\.[^.]+$/, '') || 'Engineering Documents';
    }
    if (['openapi', 'architecture'].includes(this.selectedSource) && this.selectedFiles.length > 0) {
      return this.selectedFiles[0].replace(/\.[^.]+$/, '');
    }

    const intent = sourceText.trim().replace(/\s+/g, ' ');
    const firstSentence = intent.split(/[.!?](?:\s|$)/, 1)[0].trim();
    const title = firstSentence.length >= 3 ? firstSentence : intent;
    return title.length > 120 ? `${title.slice(0, 117).trimEnd()}...` : title;
  }
}
