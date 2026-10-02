import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, timeout } from 'rxjs';
import {
  ApprovalGate,
  BlueprintUpdate,
  BuildCreateRequest,
  BuildState,
} from '../shared/models/build.models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api';

  createBuild(request: BuildCreateRequest): Observable<BuildState> {
    return this.http.post<BuildState>(`${this.baseUrl}/builds`, request).pipe(timeout({ first: 30_000 }));
  }

  getBuilds(): Observable<BuildState[]> {
    return this.http.get<BuildState[]>(`${this.baseUrl}/builds`);
  }

  startBuild(buildId: string): Observable<BuildState> {
    return this.http.post<BuildState>(`${this.baseUrl}/builds/${buildId}/start`, {});
  }

  getBuild(buildId: string): Observable<BuildState> {
    return this.http.get<BuildState>(`${this.baseUrl}/builds/${buildId}`);
  }

  approve(buildId: string, gate: Exclude<ApprovalGate, null>): Observable<BuildState> {
    return this.http.post<BuildState>(`${this.baseUrl}/builds/${buildId}/approve`, { gate });
  }

  updateBlueprint(buildId: string, blueprint: BlueprintUpdate): Observable<BuildState> {
    return this.http.put<BuildState>(`${this.baseUrl}/builds/${buildId}/blueprint`, blueprint);
  }

  refine(buildId: string, text: string): Observable<BuildState> {
    return this.http.post<BuildState>(`${this.baseUrl}/builds/${buildId}/refine`, { text });
  }
}
