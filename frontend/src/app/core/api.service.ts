import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, timeout } from 'rxjs';
import {
  ApprovalGate,
  BlueprintUpdate,
  BuildCreateRequest,
  BuildState,
  SkillRecipe,
} from '../shared/models/build.models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api';

  getDeploymentStatus(): Observable<DeploymentSetupStatus> {
    return this.http.get<DeploymentSetupStatus>(`${this.baseUrl}/integrations/deployment-status`);
  }

  createBuild(request: BuildCreateRequest): Observable<BuildState> {
    return this.http.post<BuildState>(`${this.baseUrl}/builds`, request).pipe(timeout({ first: 30_000 }));
  }

  getBuilds(): Observable<BuildState[]> {
    return this.http.get<BuildState[]>(`${this.baseUrl}/builds`);
  }

  getSkills(): Observable<SkillRecipe[]> {
    return this.http.get<SkillRecipe[]>(`${this.baseUrl}/skills`);
  }

  decideSkill(recipeId: string, decision: 'submit' | 'approve' | 'reject' | 'deprecate', reason = ''): Observable<SkillRecipe> {
    return this.http.post<SkillRecipe>(`${this.baseUrl}/skills/${encodeURIComponent(recipeId)}/decision`, { decision, reason });
  }

  startBuild(buildId: string): Observable<BuildState> {
    return this.http.post<BuildState>(`${this.baseUrl}/builds/${buildId}/start`, {});
  }

  getBuild(buildId: string): Observable<BuildState> {
    return this.http.get<BuildState>(`${this.baseUrl}/builds/${buildId}`).pipe(timeout({ first: 30_000 }));
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

  runSecurityReview(buildId: string): Observable<BuildState> {
    return this.http.post<BuildState>(`${this.baseUrl}/builds/${buildId}/security-review`, {});
  }

  prepareDeployment(buildId: string): Observable<BuildState> {
    return this.http.post<BuildState>(`${this.baseUrl}/builds/${buildId}/deployment-preflight`, {});
  }
}

export interface DeploymentSetupStatus {
  status: 'configured' | 'setup_required';
  github: {
    repository: boolean;
    app_identity: boolean;
    branch_publishing_enabled: boolean;
    contents_permission: string;
  };
  azureContainerApps: {
    subscription: boolean;
    resource_group: boolean;
    container_registry: boolean;
    container_apps_environment: boolean;
    managed_identity: boolean;
    deployment_enabled: boolean;
  };
  validation: { isolated_validation: boolean };
  branchPattern: string;
  branchPublishingImplemented: boolean;
  deploymentImplemented: boolean;
  note: string;
}
