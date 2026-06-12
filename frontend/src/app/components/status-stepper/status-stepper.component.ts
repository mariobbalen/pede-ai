import { Component, Input } from '@angular/core';

import { OrderStatus, STATUS_FLOW, STATUS_MESSAGES } from '../../models/order.model';

interface StepView {
  status: OrderStatus;
  label: string;
  done: boolean;
  active: boolean;
}

@Component({
  selector: 'app-status-stepper',
  imports: [],
  templateUrl: './status-stepper.component.html',
  styleUrl: './status-stepper.component.scss',
})
export class StatusStepperComponent {
  @Input() status: OrderStatus = 'created';

  // Full flow including the terminal "delivered" step.
  private readonly steps: OrderStatus[] = [...STATUS_FLOW, 'delivered'];

  get stepViews(): StepView[] {
    const currentIndex = this.steps.indexOf(this.status);
    return this.steps.map((step, index) => ({
      status: step,
      label: STATUS_MESSAGES[step],
      done: index < currentIndex,
      active: index === currentIndex,
    }));
  }
}
