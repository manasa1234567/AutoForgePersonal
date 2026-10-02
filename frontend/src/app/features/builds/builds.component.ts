import { ChangeDetectionStrategy, ChangeDetectorRef, Component, DestroyRef, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ApiService } from '../../core/api.service';
import { BuildState } from '../../shared/models/build.models';

@Component({
  selector: 'app-builds',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './builds.component.html',
  styleUrl: './builds.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BuildsComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  builds: BuildState[] = [];
  loading = true;
  errorMessage = '';

  ngOnInit(): void {
    this.api.getBuilds().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (builds) => {
        this.builds = builds;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.errorMessage = 'Unable to load builds. Check that the FastAPI service is running.';
        this.loading = false;
        this.cdr.markForCheck();
      },
    });
  }

  statusClass(status: BuildState['status']): string {
    return status.toLowerCase().replaceAll(' ', '-');
  }

  lastActivity(build: BuildState): string {
    return build.audit.length ? build.audit[build.audit.length - 1].time : 'No activity yet';
  }
}
